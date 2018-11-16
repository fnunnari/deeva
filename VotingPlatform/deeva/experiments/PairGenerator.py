import math


# This class is an helper to generate the senquence of pairs as required by the "prefmod" R package.
# The prefmod package is ised to perform ranking from pariwise comparisons.
# This class helps in constructing the sequence of pairs as the package need as input in the dataframe of the llbtPC.fit() function.
# The sequence is defined as in the following example (Beware: indices start from 0, while normally in R we count from 1)
# i,j = 0,1 ; 0,2 ; 1,2 ; 0,3 ; 1,3 ; 2,3 ; 0,4 ; ... ; N-2,N-1
# Where N is the number of items
# Essentially we increment the i until it reaches the j. When j is reached, we increment j and reset i to 0, until j reaches the number of items.
#
# There are also two static methods to convert from pair to sequential index:
# 0 <-> 0,1
# 1 <-> 0,2
# 2 <-> 1,2
# 3 <-> 0,3
# 4 <-> 1,3
# ...


class PairGenerator:
    def __init__(self, N):
        self.reset(N)

    def reset(self, N):
        self.num_of_items = N
        self.last_pair = (-1, 1)
        self.num_of_pairs = int(N * (N - 1) / 2)

    def setLastPair(self, i, j):
        self.last_pair = (i, j)

    def getNumOfItems(self):
        return self.num_of_items

    def getNumOfPairs(self):
        return self.num_of_pairs

    def hasNextPair(self):
        i, j = self.last_pair
        return (j - i > 1) or (j - i == 1 and j < self.num_of_items - 1)

    def getNextPair(self):
        """
        :return: The next element if the sequence of pairs, or None if there are no more pairs available
        """
        # Both i and j will range in [0,N-1]
        # Additionally, i will range in [0,j-1]
        i, j = self.last_pair

        i += 1

        # If the first element reached the second, switch to the next j, unless we are at the end.
        if (j == i):
            j += 1
            i = 0

        self.last_pair = (int(i), int(j))
        return self.last_pair

    def getNextPairAB(self, a, b):
        """
        :param a:
        :param b:
        :return: Returns the pair which follows the provided one.
        """
        self.last_pair = a, b
        return self.getNextPair()




        # This is an example of sequence, divided by "line" (j == line_number)
        # 0,1
        # 0,2	1,2
        # 0,3	1,3		2,3
        # 0,4	1,4		2,4		3,4


    @staticmethod
    def pairToIndex(a, b):
        """This method takes as input the pair a,b (b in [1,N-1], 0<=a<b) and returns the corresponding sequential
         index in [0,num_of_items-1]. Constant complexity.
        :param a:
        :param b:
        :return:
        """
        # b corresponds to the line number of the above table

        # m = Number of elements in the previous lines
        m = b * (b - 1) / 2

        # a + 1 is the offset in the current line
        # n = (m-1) + (a+1) = m+a
        return m + a

    # This method takes as input the sequential index, [0,num_of_items-1], and returns the corresponding pair. Constant complexity.
    @staticmethod
    def indexToPair(idx):
        # We know that given a line number l, the sum of the elements on all lines is 1+2+3+4+... = sum(1,l) i = l(l+1)/2
        # The following is the first root of the equation l(l+1)/2 = y ==> l^2 + l - 2y = 0
        # (i.e.) given a number of elements, we get in which line number we are.
        l1 = (-1 + math.sqrt(1 + 8 * idx)) / 2.0
        # print(str(idx) +"--> l1="+str(l1))
        # l2 = ( -1 - math.sqrt(1+8*idx) ) / 2.0	# negative solution. Not needed.

        b = math.floor(l1)  # take the smaller integer solution
        b = int(b) + 1  # and add 1 to get b, which is "line number + 1"

        # m = Number of elements in the previous lines
        m = b * (b - 1) / 2

        # a is the number of elements left on this line
        a = idx - m

        return int(a), int(b)  # Test method, generaet and prints out a couple of sequences.


def test():
    gen = PairGenerator(5)

    print("Generator initialized with " + str(gen.getNumOfItems()) + " items")
    print("Possible number of pairs = " + str(gen.getNumOfPairs()))
    while (gen.hasNextPair()):
        i, j = gen.getNextPair()
        idx = PairGenerator.pairToIndex(i, j)
        print("Next couple: " + str(i) + " " + str(j) + " idx " + str(idx))

    gen.reset(10)

    print("Generator initialized with " + str(gen.getNumOfItems()) + " items")
    print("Possible number of pairs = " + str(gen.getNumOfPairs()))
    while (gen.hasNextPair()):
        i, j = gen.getNextPair()
        idx = PairGenerator.pairToIndex(i, j)
        print("Next couple: " + str(i) + " " + str(j) + " idx " + str(idx))

    print("Test index to pair...")
    for idx in range(0, 11):
        print(str(idx) + " --> " + str(PairGenerator.indexToPair(idx)))

    print("Performance tests...")

    class PerfMeter:

        def before(self):
            import time
            self.before_time = time.time()
            self.iter_count = 0

        def iteration(self):
            self.iter_count += 1

        def after(self):
            import time
            after = time.time()
            elapsed = after - self.before_time
            rate = self.iter_count / elapsed
            print("Performed " + str(self.iter_count) + " iterations in " + str(elapsed) + " seconds: " + str(
                rate) + " iter/sec")

    perf_meter = PerfMeter()

    print("Pair generation")
    gen.reset(3000)
    perf_meter.before()
    while (gen.hasNextPair()):
        gen.getNextPair()
        perf_meter.iteration()

    perf_meter.after()
    # v1
    # Generated 4498500 in 3.12176394463 seconds: 1441012.22251 pairs/sec
    # After simplifying tests (v2)
    # Generated 4498500 in 2.98786902428 seconds: 1505588.08417 pairs/sec
    # Generated 4498500 in 2.83154511452 seconds: 1588708.57361 pairs/sec
    # With new iteration perf_meter
    # Performed 4498500 iterations in 4.41341114044 seconds: 1019279.61317 iter/sec

    print("Test index to pair...")
    perf_meter.before()
    for idx in range(0, 3000000):
        PairGenerator.indexToPair(idx)
        perf_meter.iteration()
    perf_meter.after()
    # Performed 30000 iterations in 0.950809001923 seconds: 31552.078219 iter/sec
    # After removing factorials
    # Performed 3000000 iterations in 4.4746029377 seconds: 670450.549863 iter/sec

    print("Test PairToIndex...")
    perf_meter.before()
    for idx in range(0, 3000000):
        PairGenerator.pairToIndex(idx, idx + 1)
        perf_meter.iteration()
    perf_meter.after()


# Performed 3000 iterations in 4.87544894218 seconds: 615.3279494 iter/sec
# After removing factorials
# Performed 3000000 iterations in 1.99426984787 seconds: 1504309.96247 iter/sec


if __name__ == '__main__':
    test()
