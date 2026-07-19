package main

import (
	"errors"
	"flag"
	"fmt"
	"math"
	"math/rand"
	"os"
	"sort"
)

// 一条指向节点的引用
type entry struct {
	id  int
	age int
}

type node struct {
	id    int
	alive bool    // 是否存活
	view  []entry // 邻居列表，也叫 partial view，局部可见到的周边邻居状态，也就是局部视图
}

type network struct {
	nodes      []node
	viewSize   int // 每个节点的邻居列表大小
	healOldest int // 保护最老的引用不被发送出去
	rng        *rand.Rand
}

// 统计指标
type metrics struct {
	alive          int     // 存活节点数
	references     int     // 总引用数
	deadReferences int     // 指向已死亡节点的引用数
	component      int     // 最大连通分量大小
	minIndegree    int     // 最小入度
	maxIndegree    int     // 最大入度
	meanIndegree   float64 // 平均入度
	stddevIndegree float64 // 入度标准差
	meanAge        float64 // 平均引用年龄
}

// 初始环形网络拓扑，节点 i 的邻居是 (i+1)%N, (i+2)%N, ..., (i+c)%N，保证图初始是连通的，可以互换和观察混合过程
func newNetwork(nodeCount, viewSize, healOldest int, seed int64) (*network, error) {
	if err := validate(nodeCount, viewSize, healOldest, 1, 0, 0); err != nil {
		return nil, err
	}

	n := &network{
		nodes:      make([]node, nodeCount),
		viewSize:   viewSize,
		healOldest: healOldest,
		rng:        rand.New(rand.NewSource(seed)),
	}
	// Start from a local ring so the experiment can show view mixing over time.
	for id := range n.nodes {
		n.nodes[id] = node{id: id, alive: true, view: make([]entry, 0, viewSize)}
		for offset := 1; offset <= viewSize; offset++ {
			n.nodes[id].view = append(n.nodes[id].view, entry{id: (id + offset) % nodeCount})
		}
	}
	return n, nil
}

// 模拟一轮协议运行，每个节点随机选择一个邻居进行交换
func (n *network) runRound() {
	// Random order serializes the active threads without favoring low node IDs.
	order := n.rng.Perm(len(n.nodes))
	for _, id := range order {
		if !n.nodes[id].alive {
			continue
		}
		n.exchange(id)
	}
}

func (n *network) exchange(activeID int) {
	peerID, ok := n.selectLivePeer(activeID)
	if !ok {
		return
	}

	activeBuffer, activeSent := n.makeBuffer(activeID)
	peerBuffer, peerSent := n.makeBuffer(peerID)
	// Both sides build from snapshots taken before this exchange.
	activeView := append([]entry(nil), n.nodes[activeID].view...)
	peerView := append([]entry(nil), n.nodes[peerID].view...)

	n.nodes[activeID].view = n.buildView(activeID, activeView, peerBuffer, activeSent)
	n.nodes[peerID].view = n.buildView(peerID, peerView, activeBuffer, peerSent)
	incrementAges(n.nodes[activeID].view)
	incrementAges(n.nodes[peerID].view)
}

// 从节点的邻居列表中随机选择一个存活的邻居节点进行交换
func (n *network) selectLivePeer(nodeID int) (int, bool) {
	view := &n.nodes[nodeID].view
	for len(*view) > 0 {
		index := n.rng.Intn(len(*view))
		candidate := (*view)[index].id
		if n.nodes[candidate].alive {
			return candidate, true
		}
		// 删除已死亡节点的引用
		*view = append((*view)[:index], (*view)[index+1:]...)
	}
	return 0, false
}

// 构建一个缓冲区，包含节点自身和部分邻居列表，用于交换
func (n *network) makeBuffer(nodeID int) ([]entry, map[int]bool) {
	view := append([]entry(nil), n.nodes[nodeID].view...)                            // 复制邻居列表
	n.rng.Shuffle(len(view), func(i, j int) { view[i], view[j] = view[j], view[i] }) // 随机打乱邻居列表

	// 将最老的引用移动到缓冲区的末尾，以保护它们不被发送出去
	oldest := min(n.healOldest, len(view))
	if oldest > 0 {
		view = moveOldestToEnd(view, oldest)
	}
	// 发送的邻居数量限制为视图大小的一半，如果减去保护的最老引用数量小于他，就取他，避免老引用被发送出去
	limit := min(n.viewSize/2, len(view)-oldest)
	if limit < 0 {
		limit = 0
	}

	buffer := make([]entry, 0, limit+1) // +1 for the node itself
	buffer = append(buffer, entry{id: nodeID})
	sent := make(map[int]bool, limit)
	for _, item := range view[:limit] { // 标记已发送的邻居，用于后续接受预留位置时优先淘汰
		buffer = append(buffer, item)
		sent[item.id] = true
	}
	return buffer, sent
}

func moveOldestToEnd(view []entry, count int) []entry {
	indices := make([]int, len(view))
	for i := range indices {
		indices[i] = i
	}
	sort.SliceStable(indices, func(i, j int) bool {
		return view[indices[i]].age > view[indices[j]].age
	})

	isOldest := make([]bool, len(view))
	for _, index := range indices[:count] {
		isOldest[index] = true
	}
	result := make([]entry, 0, len(view))
	for index, item := range view {
		if !isOldest[index] {
			result = append(result, item)
		}
	}
	for index, item := range view {
		if isOldest[index] {
			result = append(result, item)
		}
	}
	return result
}

// 构建节点的邻居列表，结合当前邻居列表、接收到的邻居列表和已发送的邻居列表，确保不超过视图大小，并优先淘汰已发送的邻居，最后按年龄排序，淘汰最老的引用。
// 交换会多一个自身引用来替代对方的最老引用，保证视图的新陈代谢，自身存活可以维持，老节点被淘汰，保证网络的活性和连通性。
func (n *network) buildView(nodeID int, current, received []entry, sent map[int]bool) []entry {
	// 先保留当前 view，再加入对方发来的缓冲区；后续统一去重和裁剪。
	candidates := make([]entry, 0, len(current)+len(received))
	candidates = append(candidates, current...)
	candidates = append(candidates, received...)

	// 去重和裁剪，保证视图大小不超过 viewSize
	unique := make(map[int]entry, len(candidates))
	for _, item := range candidates {
		// 节点不能引用自身；
		if item.id == nodeID {
			continue
		}
		previous, exists := unique[item.id]
		// 同一节点有多个引用时，保留 age 更小的新鲜引用。
		if !exists || item.age < previous.age {
			unique[item.id] = item
		}
	}
	result := make([]entry, 0, len(unique))
	for _, item := range unique {
		result = append(result, item)
	}
	sort.Slice(result, func(i, j int) bool { return result[i].id < result[j].id })
	n.rng.Shuffle(len(result), func(i, j int) { result[i], result[j] = result[j], result[i] })

	excess := len(result) - n.viewSize
	if excess <= 0 {
		return result
	}

	kept := make([]entry, 0, len(result)-excess)
	// 优先移除本轮已发送给对方的引用，相当于用收到的新引用完成交换。
	for _, item := range result {
		if excess > 0 && sent[item.id] {
			excess--
			continue
		}
		kept = append(kept, item)
	}
	if excess > 0 {
		// 对方还会附带自己的 age=0 引用，导致超容，来替换 age 最大、最久未被刷新且更可能已经失效的引用。
		sort.SliceStable(kept, func(i, j int) bool { return kept[i].age < kept[j].age })
		kept = kept[:len(kept)-excess]
	}
	return kept
}

func incrementAges(view []entry) {
	for i := range view {
		view[i].age++
	}
}

// 模拟节点失败，随机选择存活的节点将其标记为死亡
func (n *network) fail(count int) []int {
	failed := make([]int, 0, count)
	for id := len(n.nodes) - 1; id >= 0 && len(failed) < count; id-- {
		if n.nodes[id].alive {
			n.nodes[id].alive = false
			failed = append(failed, id)
		}
	}
	sort.Ints(failed)
	return failed
}

// 计算网络的统计指标，包括存活节点数、引用数、最大连通分量大小、入度统计和平均引用年龄
func (n *network) measure() metrics {
	indegree := make([]int, len(n.nodes))
	result := metrics{minIndegree: math.MaxInt}
	totalAge := 0
	start := -1

	for _, current := range n.nodes {
		if !current.alive {
			continue
		}
		result.alive++
		if start < 0 {
			start = current.id
		}
		for _, item := range current.view {
			result.references++
			totalAge += item.age
			if n.nodes[item.id].alive {
				indegree[item.id]++
			} else {
				result.deadReferences++
			}
		}
	}

	if result.alive == 0 {
		result.minIndegree = 0
		return result
	}
	for id, degree := range indegree {
		if !n.nodes[id].alive {
			continue
		}
		result.meanIndegree += float64(degree)
		result.minIndegree = min(result.minIndegree, degree)
		result.maxIndegree = max(result.maxIndegree, degree)
	}
	result.meanIndegree /= float64(result.alive)
	for id, degree := range indegree {
		if n.nodes[id].alive {
			delta := float64(degree) - result.meanIndegree
			result.stddevIndegree += delta * delta
		}
	}
	result.stddevIndegree = math.Sqrt(result.stddevIndegree / float64(result.alive))
	if result.references > 0 {
		result.meanAge = float64(totalAge) / float64(result.references)
	}
	result.component = n.componentFrom(start)
	return result
}

func (n *network) componentFrom(start int) int {
	if start < 0 {
		return 0
	}
	seen := map[int]bool{start: true}
	queue := []int{start}
	// A stored reference permits contact, so connectivity ignores edge direction.
	for len(queue) > 0 {
		id := queue[0]
		queue = queue[1:]
		for _, item := range n.nodes[id].view {
			if n.nodes[item.id].alive && !seen[item.id] {
				seen[item.id] = true
				queue = append(queue, item.id)
			}
		}
		for source := range n.nodes {
			if !n.nodes[source].alive || seen[source] {
				continue
			}
			for _, item := range n.nodes[source].view {
				if item.id == id {
					seen[source] = true
					queue = append(queue, source)
					break
				}
			}
		}
	}
	return len(seen)
}

// Validate command-line arguments.
func validate(nodes, viewSize, healOldest, rounds, failRound, failures int) error {
	switch {
	case nodes < 3:
		return errors.New("nodes must be at least 3")
	case viewSize < 2 || viewSize >= nodes:
		return errors.New("view must be between 2 and nodes - 1")
	case healOldest < 0 || healOldest >= viewSize:
		return errors.New("heal-oldest must be between 0 and view - 1")
	case rounds < 1:
		return errors.New("rounds must be positive")
	case failRound < 0 || failRound > rounds:
		return errors.New("fail-round must be between 0 and rounds")
	case failures < 0 || failures >= nodes-viewSize:
		return errors.New("failures must leave more live nodes than the view size")
	default:
		return nil
	}
}

// 打印网络的统计指标
func printMetrics(round int, event string, value metrics) {
	fmt.Printf("%5d  %-9s %5d  %5d/%-5d %7.2f %7.2f %4d..%-4d %7.2f %7d\n",
		round, event, value.alive, value.component, value.alive,
		value.meanIndegree, value.stddevIndegree, value.minIndegree,
		value.maxIndegree, value.meanAge, value.deadReferences)
}

func main() {
	nodeCount := flag.Int("nodes", 100, "number of nodes")
	viewSize := flag.Int("view", 10, "partial-view size c")
	rounds := flag.Int("rounds", 30, "number of protocol rounds")
	healOldest := flag.Int("heal-oldest", 1, "oldest entries protected from sending")
	failRound := flag.Int("fail-round", 15, "round in which nodes leave; 0 disables failure injection")
	failures := flag.Int("failures", 10, "number of nodes that leave")
	reportEvery := flag.Int("report-every", 1, "print metrics every N rounds")
	seed := flag.Int64("seed", 20260718, "random seed")
	flag.Parse()

	if *failRound == 0 {
		*failures = 0
	}
	if err := validate(*nodeCount, *viewSize, *healOldest, *rounds, *failRound, *failures); err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(2)
	}
	if *reportEvery < 1 {
		fmt.Fprintln(os.Stderr, "error: report-every must be positive")
		os.Exit(2)
	}

	n, _ := newNetwork(*nodeCount, *viewSize, *healOldest, *seed)
	fmt.Printf("nodes=%d view=%d rounds=%d H=%d seed=%d\n", *nodeCount, *viewSize, *rounds, *healOldest, *seed)
	fmt.Println("round  event     alive  component   indeg    stddev range       age deadrefs")
	printMetrics(0, "initial", n.measure()) // 打印初始指标

	for round := 1; round <= *rounds; round++ {
		event := "exchange"
		if round == *failRound && *failures > 0 {
			failed := n.fail(*failures)
			event = fmt.Sprintf("leave:%d", len(failed))
		}
		n.runRound()
		if round%*reportEvery == 0 || round == *failRound || round == *rounds {
			printMetrics(round, event, n.measure())
		}
	}
}
