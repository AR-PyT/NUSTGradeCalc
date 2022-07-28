#!/usr/bin/env python3.6
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from math import sqrt
import os
import scipy.stats as stats
import numpy as np

grade_map = {'0': "A", '1': "B+", '2': "B", '3': "C+", '4': "C", '5': "D+", '6': "D", '7': "F"}

l1_weights = np.loadtxt("GradeApp/params/w1.txt")
l1_bias = np.loadtxt("GradeApp/params/b1.txt")

l2_weights = np.loadtxt("GradeApp/params/w2.txt")
l2_bias = np.loadtxt("GradeApp/params/b2.txt")

l3_weights = np.loadtxt("GradeApp/params/w3.txt")
l3_bias = np.loadtxt("GradeApp/params/b3.txt")


def get_predict(input_data):
    return np.matmul(
        np.maximum(0, np.matmul(np.maximum(0, np.matmul(input_data, l1_weights) + l1_bias), l2_weights) + l2_bias),
        l3_weights) + l3_bias


def get_boundary(score, ch, mean, data):
    prev_grade = 0
    cur_grade = 0
    boundaries = []

    while len(boundaries) != 8 and score > 0:
        while not prev_grade < cur_grade:
            SB = list(1 if score > x > mean else 0 for x in data).count(1) if score > mean else -list(
                1 if score < x < mean else 0 for x in data).count(1)
            SB /= len(data)
            res = get_predict(np.array([[score, ch, mean, SB, score ** 2, score * ch, score * mean, score * SB,
                                         ch ** 2, ch * mean, ch * SB, mean ** 2, mean * SB, SB ** 2]]))[0]
            cur_grade = np.where(res == np.max(res))[0][0]  # gives index for grade
            score -= 1
        score += 0.9
        cur_grade = prev_grade

        while not prev_grade < cur_grade:
            SB = list(1 if score > x > mean else 0 for x in data).count(1) if score > mean else -list(
                1 if score < x < mean else 0 for x in data).count(1)
            SB /= len(data)
            res = get_predict(np.array([[score, ch, mean, SB, score ** 2, score * ch, score * mean, score * SB,
                                         ch ** 2, ch * mean, ch * SB, mean ** 2, mean * SB, SB ** 2]]))[0]
            cur_grade = np.where(res == np.max(res))[0][0]  # gives index for grade
            score -= 0.1
        boundaries.insert(0, score + 0.1)

        prev_grade = cur_grade
        if cur_grade == 7:
            boundaries.insert(0, score)
            break

    for i in range(8 - len(boundaries)):
        boundaries.insert(0, 0)

    return boundaries


def make_prediction(score, ch, data):
    mean = data.mean()
    SB = list(1 if score > x > mean else 0 for x in data).count(1) if score > mean else -list(
        1 if score < x < mean else 0 for x in data).count(1)
    SB /= len(data)
    res = get_predict(np.array([[score, ch, mean, SB,
                                 score ** 2, score * ch, score * mean, score * SB,
                                 ch ** 2, ch * mean, ch * SB,
                                 mean ** 2, mean * SB,
                                 SB ** 2]]))[0]

    grade = np.where(res == np.max(res))[0][0]

    # Special Chk for Management Tentative
    start = 95 if mean > 90 else 89

    boundaries = get_boundary(start, ch, mean, data)
    return (grade_map[str(grade)],
            (str(round(100 - (stats.norm.cdf((boundaries[8 - grade] - score) / sqrt(data.var())) * 100),
                       2)) if grade else "0") + "%",
            (str(round((stats.norm.cdf((boundaries[7 - grade] - score) / sqrt(data.var())) * 100),
                       2)) if grade != 7 else "0") + "%",
            )


def decide_boundary(ch, label, i_name, data):
    plt.clf()
    plt.cla()
    if not data.size:
        return
    mean = data.mean()
    std_deviation = sqrt(data.var())
    score = 95 if label == "Intro To Management" else 89

    boundaries = get_boundary(score, ch, mean, data)
    # Plot the new curve and save it
    x = np.linspace(mean - 3 * std_deviation, mean + 3 * std_deviation, 100)
    # if std_deviation:
    y = stats.norm.pdf(x, mean, std_deviation)

    x = [y for y in x]
    y = [x for x in y]
    for i in range(int(x[0]) + 1):
        x.insert(0, i)
        y.insert(0, 0)
    for i in range(int(x[-1]) + 1, 101):
        x.insert(-1, i)
        y.insert(-1, 0)
    x = np.array(x)
    y = np.array(y)

    plt.plot(x, y, label=label, color="black")
    plt.rcParams["figure.figsize"] = (10, 1)
    # filling colors Start from
    try:
        start = np.where(x > boundaries[-1])[0][0]
    except IndexError:
        print("Actual Was:", np.where(x > boundaries[-1]))
        print(np.where(x > boundaries[-1])[0])
        print("[-] ERROR boundaries were: ", boundaries)
        return
    plt.fill_between(x[start:], 0, y[start:], color='green', alpha=0.7)

    end = start + 3
    start = np.where(x > boundaries[-2])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='blue', alpha=0.3)

    end = start + 3
    start = np.where(x > boundaries[-3])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='red', alpha=0.3)

    end = start + 3
    start = np.where(x > boundaries[-4])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='pink', alpha=0.3)

    end = start + 3
    start = np.where(x > boundaries[-5])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='purple', alpha=0.3)

    end = start + 3
    start = np.where(x > boundaries[-6])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='brown', alpha=0.3)

    end = start + 3
    start = np.where(x > boundaries[-7])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='red', alpha=0.3)

    end = start + 3
    start = np.where(x > boundaries[-8])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='black', alpha=0.3)

    patch1 = mpatches.Patch(color='green', label='A')
    patch2 = mpatches.Patch(color='blue', label='B+')
    patch3 = mpatches.Patch(color='red', label='B')
    patch4 = mpatches.Patch(color='pink', label='C+')
    patch5 = mpatches.Patch(color='purple', label='C')
    patch6 = mpatches.Patch(color='brown', label='D+')
    patch7 = mpatches.Patch(color='red', label='D')
    patch8 = mpatches.Patch(color='black', label='F')

    plt.legend(handles=[patch1, patch2, patch3, patch4, patch5, patch6, patch7, patch8])
    plt.title(label)
    if os.path.exists("./static/GradeApp/img/" + i_name):
        os.remove("./static/GradeApp/img/" + i_name)
    plt.savefig("./static/GradeApp/img/" + i_name)

# from GradeApp import models
# d = np.array([*models.GradesA.objects.values_list("oop"),
#                                  *models.GradesB.objects.values_list("oop")])
# decide_boundary(4, "test", "tt.png", d)
