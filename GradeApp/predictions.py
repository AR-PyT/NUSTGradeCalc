#!/usr/bin/env python3.6
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from math import sqrt
import scipy.stats as stats
import numpy as np

grade_map = {'0': "A", '1': "B+", '2': "B", '3': "C+", '4': "C", '5': "D+", '6': "D", '7': "F"}
model = tf.keras.models.load_model("GradeApp/simpleModel.h5", compile=True)


def make_prediction(score, ch, data):
    mean = data.mean()
    SB = list(1 if score > x > mean else 0 for x in data).count(1) if score > mean else -list(
        1 if score < x < mean else 0 for x in data).count(1)
    SB /= len(data)

    res = model.predict(np.array([[score, ch, mean, SB,
                                   score ** 2, score * ch, score * mean, score * SB,
                                   ch ** 2, ch * mean, ch * SB,
                                   mean ** 2, mean * SB,
                                   SB ** 2]]))[0]
    grade = np.where(res == np.max(res))[0][0]
    return grade_map[str(grade)]


def decide_boundary(ch, label, i_name, data):
    if not data.size:
        return
    mean = data.mean()
    std_deviation = sqrt(data.var())
    score = 95
    prev_grade = 0
    cur_grade = 0
    boundaries = []

    while len(boundaries) != 8 and score > 0:
        while not prev_grade < cur_grade:
            SB = list(1 if score > x > mean else 0 for x in data).count(1) if score > mean else -list(
                1 if score < x < mean else 0 for x in data).count(1)
            SB /= len(data)
            res = model.predict(np.array([[score, ch, mean, SB, score ** 2, score * ch, score * mean, score * SB,
                                           ch ** 2, ch * mean, ch * SB, mean ** 2, mean * SB, SB ** 2]]))[0]
            cur_grade = np.where(res == np.max(res))[0][0]  # gives index for grade
            score -= 10
        score += 8
        cur_grade = prev_grade
        while prev_grade < cur_grade:
            SB = list(1 if score > x > mean else 0 for x in data).count(1) if score > mean else -list(
                1 if score < x < mean else 0 for x in data).count(1)
            SB /= len(data)
            res = model.predict(np.array([[score, ch, mean, SB, score ** 2, score * ch, score * mean, score * SB,
                                           ch ** 2, ch * mean, ch * SB, mean ** 2, mean * SB, SB ** 2]]))[0]
            cur_grade = np.where(res == np.max(res))[0][0]  # gives index for grade
            score -= 2
        score += 1.5
        while not prev_grade < cur_grade:
            SB = list(1 if score > x > mean else 0 for x in data).count(1) if score > mean else -list(
                1 if score < x < mean else 0 for x in data).count(1)
            SB /= len(data)
            res = model.predict(np.array([[score, ch, mean, SB, score ** 2, score * ch, score * mean, score * SB,
                                           ch ** 2, ch * mean, ch * SB, mean ** 2, mean * SB, SB ** 2]]))[0]
            cur_grade = np.where(res == np.max(res))[0][0]  # gives index for grade
            score -= 0.5
        boundaries.insert(0, score)
        prev_grade = cur_grade
        if cur_grade == 7:
            boundaries.insert(0, score)
            break

    for i in range(8 - len(boundaries)):
        boundaries.insert(0, 0)
    # Plot the new curve and save it
    x = np.linspace(0, 100, 400)
    if std_deviation:
        y = stats.norm.pdf(x, mean, std_deviation)
    else:
        y = [0] * 400
        y[int(round(mean, 0) * 4)] = 1
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

    end = start + 5
    start = np.where(x > boundaries[-2])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='blue', alpha=0.3)

    end = start + 5
    start = np.where(x > boundaries[-3])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='red', alpha=0.3)

    end = start + 5
    start = np.where(x > boundaries[-4])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='pink', alpha=0.3)

    end = start + 5
    start = np.where(x > boundaries[-5])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='purple', alpha=0.3)

    end = start + 5
    start = np.where(x > boundaries[-6])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='brown', alpha=0.3)

    end = start + 5
    start = np.where(x > boundaries[-7])[0][0]
    plt.fill_between(x[start:end], 0, y[start:end], color='red', alpha=0.3)

    end = start + 5
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
    plt.savefig("./static/GradeApp/img/" + i_name)
