# A script to run once to generate files to load into memory at the start of the baby name generator backend server
import csv
from collections import defaultdict
from itertools import product
import random
import math
from flask import Flask
import flask

from flask_cors import CORS, cross_origin


def new_lmh_count():
    res = {}
    for c in ['l', 'm', 'h']:
        res[c] = defaultdict(int)
    return res

class NameGenerator:
    def __init__(self):
        self.syl_count = defaultdict(int)
        self.syl_position_count = {0: defaultdict(int), 1: defaultdict(int), 2: defaultdict(int), 3: defaultdict(int), 4: defaultdict(int)}
        self.syl_position_usage_counts = {0: new_lmh_count(), 1: new_lmh_count(), 2: new_lmh_count(), 3: new_lmh_count(), 4: new_lmh_count()}
        self.subsequent_list = defaultdict(list)

    def parse(self):
        with open('names_split_top_50.txt', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=' ')
            for popularity_index, row in enumerate(reader):
                syllables = [x.lower() for x in row[1].split('-')]
                scale = 0
                if popularity_index < 50:
                    scale = 3
                elif popularity_index < 100:
                    scale = 2
                elif popularity_index < 150:
                    scale = 1
                for i, syl in enumerate(syllables):
                    self.syl_count[syl] += 1 + scale
                    self.syl_position_count[i][syl] += 1 + scale
        # print(self.syl_count)

    def find_freq_count(self, syl):
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
        total_frequency_high_count = strength * 2 + math.ceil(speed / 2)
        total_frequency_middle_count = speed + compassion
        total_frequency_low_count = (intelligence * 2) + math.ceil(honesty / 2)
        syllable_2_count = strength + speed
        syllable_3_count = strength + speed + compassion
        syllable_4_count = math.floor(intelligence/1.1 + honesty)
        syllable_5_count = math.floor(intelligence + compassion/1.8)
        deviation_high_count = math.ceil(intelligence * 1.9)
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

        return {'total_frequency': total_frequency, 'num_syllables': num_syllables, 'deviation': deviation}

    def generate_name(self, intelligence, strength, speed, honesty, compassion):
        params = self.compute_params(intelligence, strength, speed, honesty, compassion)
        # print(params)
        name = []

        for i in range(params['num_syllables']):
            if i == 3:
                i = random.choice([2, 3])
            syl_choice = self.syl_position_usage_counts[i][params['total_frequency']]

            sorted_syl_choice = dict(sorted(syl_choice.items(), key=lambda item: item[1], reverse=True))
            # print('poss', i, params['deviation'], sorted_syl_choice)
            try:
                syl = self.choose_per_deviation(list(sorted_syl_choice.keys()), params['deviation'])
                # print('got', syl)
                name.append(syl)
            except IndexError:
                continue

        name = ''.join(name)
        return {'name': name.capitalize(), 'params': params}


app = Flask(__name__)
CORS(app,)
p = NameGenerator()
p.parse()
p.parse_counts()


@app.route("/api/generate_name/<int:intelligence>/<int:strength>/<int:speed>/<int:honesty>/<int:compassion>")
@cross_origin()
def run(intelligence, strength, speed, honesty, compassion):
    res = p.generate_name(intelligence, strength, speed, honesty, compassion)
    response = flask.jsonify(res)
    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1",debug=True)