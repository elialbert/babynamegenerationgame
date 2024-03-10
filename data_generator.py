# A script to run once to generate files to load into memory at the start of the baby name generator backend server
import csv
from collections import defaultdict
from itertools import product
import random
import math
from flask import Flask



def new_lmh_count():
    res = {}
    for c in ['l', 'm', 'h']:
        res[c] = defaultdict(int)
    return res

class NameGenerator:
    def __init__(self):
        self.all_names = []
        # self.all_syllables = []
        self.syl_count = defaultdict(int)
        self.syl_position_count = {0: defaultdict(int), 1: defaultdict(int), 2: defaultdict(int), 3: defaultdict(int), 4: defaultdict(int)}
        self.syl_position_usage_counts = {0: new_lmh_count(), 1: new_lmh_count(), 2: new_lmh_count(), 3: new_lmh_count(), 4: new_lmh_count()}
        self.subsequent_list = defaultdict(list)

    def parse(self):
        with open('names_split_top_50.txt', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ')
            for row in reader:
                self.all_names.append(row[0])
                syllables = [x.lower() for x in row[1].split('-')]
                # self.all_syllables.extend(syllables)
                for i, syl in enumerate(syllables):
                    self.syl_count[syl] += 1
                    self.syl_position_count[i][syl] += 1
                    # if i > 0:
                    #     self.subsequent_list[syllables[i-1]].append(syl)
        # self.all_syllables = list(set(self.all_syllables))
        # print(self.subsequent_list)

    def find_freq_count(self, syl):
        # look up in syl_count_high or null if not found
        # print(syl, self.syl_count_middle)
        ch = self.syl_count_high.get(syl)
        cm = self.syl_count_middle.get(syl)
        cl = self.syl_count_low.get(syl)

        if ch:
            return ['h', ch]
        elif cm:
            return ['m', cm]
        elif cl:
            return ['l', cl]

    def parse_counts(self):
        first_third = len(self.syl_count) // 3
        # order self.syl_count by frequency
        self.syl_count_high = dict(sorted(self.syl_count.items(), key=lambda item: item[1], reverse=True)[:first_third])
        self.syl_count_middle = dict(sorted(self.syl_count.items(), key=lambda item: item[1], reverse=True)[first_third:first_third*2])
        self.syl_count_low = dict(sorted(self.syl_count.items(), key=lambda item: item[1], reverse=True)[first_third*2:])

        # print('a', self.syl_count_high)
        # print('b', self.syl_count_middle)
        # print('c', self.syl_count_low)

        for position, entries in self.syl_position_count.items():
            # ie position is 0 and combo is lh, meaning it's a first syllable and it has
            # low overall frequency and high top frequency
            for syl in entries:
                combo, combo_count = self.find_freq_count(syl)
                self.syl_position_usage_counts[position][combo][syl] += combo_count

        # for i, v in self.syl_position_usage_counts.items():
        #     print(i)
        #     for k, vv in v.items():
        #         print(k ,vv)

    def choose_per_deviation(self, choices, deviation):
        first_third = len(choices) // 3
        second_third = first_third * 2
        if deviation == 'l':
            return random.choice(choices[:first_third])
        elif deviation == 'm':
            return random.choice(choices[first_third:second_third])
        else:
            return random.choice(choices[second_third:])

    def compute_params(self, intelligence, strength, speed, honesty, compassion):
        # accepts 5 scores as input
        total_frequency_high_count = strength
        total_frequency_middle_count = speed + compassion
        total_frequency_low_count = intelligence + honesty
        top_frequency_high_count = strength + honesty
        top_frequency_middle_count = compassion
        top_frequency_low_count = intelligence + speed
        syllable_2_count = strength + speed
        syllable_3_count = strength + speed + compassion
        syllable_4_count = math.floor(intelligence/1.1 + honesty)
        syllable_5_count = math.floor(intelligence + compassion/1.8)
        deviation_high_count = intelligence
        deviation_middle_count = honesty + compassion
        deviation_low_count = strength + speed
        total_frequency_total_count = total_frequency_high_count + total_frequency_middle_count + total_frequency_low_count
        random_total_frequency = random.randint(0, total_frequency_total_count)
        if random_total_frequency < total_frequency_low_count:
            total_frequency = 'l'
        elif random_total_frequency < total_frequency_low_count + total_frequency_middle_count:
            total_frequency = 'm'
        else:
            total_frequency = 'h'

        total_top_frequency_total_count = top_frequency_high_count + top_frequency_middle_count + top_frequency_low_count
        random_total_top_frequency = random.randint(0, total_top_frequency_total_count)
        if random_total_top_frequency < top_frequency_low_count:
            total_top_frequency = 'l'
        elif random_total_top_frequency < top_frequency_low_count + top_frequency_middle_count:
            total_top_frequency = 'm'
        else:
            total_top_frequency = 'h'

        syllable_total_count = syllable_2_count + syllable_3_count + syllable_4_count + syllable_5_count
        random_syllable = random.randint(1, syllable_total_count)
        if random_syllable < syllable_2_count:
            num_syllables = 2
        elif random_syllable < syllable_2_count + syllable_3_count:
            num_syllables = 2
        elif random_syllable < syllable_2_count + syllable_3_count + syllable_4_count:
            num_syllables = 3
        elif random_syllable < syllable_2_count + syllable_3_count + syllable_4_count + syllable_5_count:
            num_syllables = 4
        else:
            num_syllables = 4

        deviation_total_count = deviation_high_count + deviation_middle_count + deviation_low_count
        random_deviation = random.randint(0, deviation_total_count)
        if random_deviation < deviation_low_count:
            deviation = 'l'
        elif random_deviation < deviation_low_count + deviation_middle_count:
            deviation = 'm'
        else:
            deviation = 'h'

        return {'total_frequency': total_frequency, 'total_top_frequency': total_top_frequency, 'num_syllables': num_syllables, 'deviation': deviation}

    def generate_name(self, intelligence, strength, speed, honesty, compassion):
        params = self.compute_params(intelligence, strength, speed, honesty, compassion)
        print(params)
        name = []

        for i in range(params['num_syllables']):
            syl_choice = self.syl_position_usage_counts[i][params['total_frequency']]
            sorted_syl_choice = dict(sorted(syl_choice.items(), key=lambda item: item[1], reverse=True))
            try:
                syl = self.choose_per_deviation(list(sorted_syl_choice.keys()), params['deviation'])
            except IndexError:
                syl_choice = self.syl_position_usage_counts[i-1][params['total_frequency']]
                sorted_syl_choice = dict(sorted(syl_choice.items(), key=lambda item: item[1], reverse=True))
                syl = self.choose_per_deviation(list(sorted_syl_choice.keys()), params['deviation'])
            name.append(syl)
        name = ''.join(name)
        return name.capitalize()


app = Flask(__name__)

@app.route("/api/generate_name/<int:intelligence>/<int:strength>/<int:speed>/<int:honesty>/<int:compassion>")
def run(intelligence, strength, speed, honesty, compassion):
    p = NameGenerator()
    p.parse()
    p.parse_counts()
    return p.generate_name(intelligence, strength, speed, honesty, compassion)


if __name__ == "__main__":
    app.run(debug=True)