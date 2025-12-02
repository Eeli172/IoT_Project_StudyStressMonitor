class Hrv:
    def __init__(self, ppi):
        self.ppi = ppi
        self.mean_hr = None # mean heart rate (bpm)
        self.mean_ppi = None # mean PPI (ms)
        self.rmssd = None # root mean square of successive differences
        self.sdnn = None # standard deviation of NN intervals

        # now calculate the measures
        self.calc_means()
        self.calc_sdnn()
        self.calc_rmssd()


    def calc_means(self):
        self.mean_ppi = sum(self.ppi) / len(self.ppi) # calculate mean ppi
        
        self.mean_hr = 60000 / self.mean_ppi # calculate mean heart rate - 60000 ms = 1 minute, so bpm = 60000 / mean_ppi


    def calc_sdnn(self):
        # calculate squared differences from mean
        sum_sq_diff = 0
        for x in self.ppi:
            diff = x - self.mean_ppi  # difference from mean
            sq_diff = diff * diff  # square the difference
            sum_sq_diff += sq_diff  # add to the sum

        # variance = sum of squared differences divided by (n-1)
        variance = sum_sq_diff / (len(self.ppi) - 1)

        # standard deviation = square root of variance
        self.sdnn = variance ** 0.5


    def calc_rmssd(self): # root mean square of successive differences
        squared_diffs = []

        # calculate differences between successive intervals
        for i in range(len(self.ppi) - 1):
            diff = self.ppi[i+1] - self.ppi[i]  # difference between next and current
            sq_diff = diff * diff  # square it
            squared_diffs.append(sq_diff)  # add to list

        # calculate mean of squared differences
        total = 0
        for val in squared_diffs:
            total += val
        mean_sq_diff = total / len(squared_diffs)

        # take square root to get rmssd
        self.rmssd = mean_sq_diff ** 0.5




if __name__ == "__main__":
    ppi = [828, 836, 852, 760, 800, 796, 856, 824, 808, 776, 724, 816, 800, 812, 812, 812, 756, 820, 812, 800]
    hrv = Hrv(ppi)

    print(hrv.mean_hr)
    print(hrv.mean_ppi)
    print(hrv.rmssd)
    print(hrv.sdnn)
