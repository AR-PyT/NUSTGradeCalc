#!/usr/bin/env python3.6
from django.shortcuts import render
import requests
import re
from bs4 import BeautifulSoup
import numpy as np
from GradeApp import models, predictions

tables = {"A": models.GradesA,
          "B": models.GradesB,
          "C": models.GradesC}

grade_schema = {
    'Calculus-II': {
        'One Hour Test/Mid Term': 30,
        'Assignment': 10,
        'Quiz': 10,
        'Final': 50
    },
    'Islamic Studies': {
        'One Hour Test/Mid Term': 30,
        'Assignment': 10,
        'Quiz': 10,
        'Final': 50
    },
    'Introduction To Management': {
        'One Hour Test/Mid Term': 40,
        'Assignment': 10,
        'Quiz': 10,
        'Final': 40
    },
    'Applied Physics': {
        'One Hour Test/Mid Term': 25,
        'Assignment': 5,
        'Quiz': 5,
        'Final': 40,
        'Lab Work': 17.5,
        'Final Lab': 7.5
    },
    'Object Oriented Programming': {
        'One Hour Test/Mid Term': 30,
        'Assignment': 7.5,
        'Quiz': 7.5,
        'Final': 30,
        'Lab Work': 17.5,
        'Final Lab': 7.5
    },
    'Digital Logic Design': {
        'One Hour Test/Mid Term': 24,
        'Assignment': 6,
        'Quiz': 9,
        'Final': 36,
        'Lab Work': 17.5,
        'Final Lab': 7.5
    }
}


def forget(request):
    uname = request.GET.get('uname')
    section = request.GET.get('section')
    if not uname or not section:
        return render(request, "invalid.html")
    try:
        try:
            tables[section.upper()].objects.get(uname=uname).delete()
        except tables[section.upper()].DoesNotExist:
            return render(request, "invalid.html")
    except tables[section.upper()].MultipleObjectsReturned:
        for a in tables[section.upper()].objects.all():
            if a.uname == uname:
                a.delete()
    return render(request, "login.html")


def add_new_record(input_data):
    try:
        temp = tables[input_data["section"].upper()].objects.get(uname=input_data["id"])
        temp.delete()
    except tables[input_data["section"].upper()].DoesNotExist:
        pass
    with requests.session() as s:
        payload = {'login': input_data["id"],
                   'password': input_data["password"]
                   }
        response = s.get("https://qalam.nust.edu.pk/")
        payload['csrf_token'] = re.findall(r'(?:csrf_token: ")(.*?)(?:")', response.content.decode('utf-8'))[0]
        if s.post("https://qalam.nust.edu.pk/web/login", data=payload).status_code != 200:
            return False

        # Get The Results Will Use BS4 and re together for extraction
        soup = BeautifulSoup(s.get("https://qalam.nust.edu.pk/student/results").content.decode('utf-8'),
                             features='html.parser')
        name = soup.find('div', class_="md-color-blue-grey-800 uk-text-bold uk-text-center uk-margin-left").text

        print("[+] Finding links")
        sub_divs = soup.find_all('h4', {'class': ['heading_c', 'md-color-grey-50', 'md-bg-blue-500']})
        print("[+] Link Archive Received")
        links = {}
        aggregates = {}
        for d in sub_divs:
            links[d.find_next('span', class_="md-list-heading").text.strip()] = "https://qalam.nust.edu.pk" + \
                                                                                d.parent['href']

        print("[+] Start Calculating Aggregates")
        # Check for Subjects one by one calculating aggregates
        for key, link in links.items():
            soup = BeautifulSoup(s.get(link).content.decode('utf-8'), features='html.parser')
            temp_score = {}

            exam_list = soup.find_all('a', class_="js-toggle-children-row")
            for exam in exam_list:
                temp_score[exam.text.strip()] = []
                score_row = exam.find_next('tr')

                while score_row:
                    score_row = score_row.find_next('tr', class_='table-child-row')
                    if not score_row or score_row.findChild('th'):
                        break
                    temp_score[exam.text.strip()].append(
                        float(re.findall(r"(.*)(?:\s*</td>, '\\n'])", str(score_row.contents))[0].strip()))

            # Calculate Aggregate Based on acquired Scores
            aggregate = 0
            for k, v in temp_score.items():
                aggregate += (sum(v) / (len(v) * 100)) * grade_schema[key][k]
            aggregates[key] = round(aggregate, 2)
            print("[+] Aggregate Calculated", aggregate)
    # Add Record to DB
    tables[input_data["section"].upper()].objects.create(uname=input_data["id"], name=name,
                                                         calc=aggregates["Calculus-II"],
                                                         istd=aggregates["Islamic Studies"],
                                                         imgt=aggregates["Introduction To Management"],
                                                         dld=aggregates["Digital Logic Design"],
                                                         oop=aggregates["Object Oriented Programming"],
                                                         ap=aggregates["Applied Physics"],
                                                         password=input_data["password"])

    # Create New Images
    #
    predictions.decide_boundary(2, "Islamic Studies", "ABC/isl.png", np.array([
        *models.GradesA.objects.values_list('istd'),
        *models.GradesB.objects.values_list('istd'),
        *models.GradesC.objects.values_list('istd')
    ]))
    predictions.decide_boundary(2, "Intro To Management", "ABC/imgt.png", np.array([
        *models.GradesA.objects.values_list('imgt'),
        *models.GradesB.objects.values_list('imgt'),
        *models.GradesC.objects.values_list('imgt')
    ]))
    predictions.decide_boundary(3, "Calculus-II", "ABC/calc.png", np.array([
        *models.GradesA.objects.values_list('calc'),
        *models.GradesB.objects.values_list('calc'),
        *models.GradesC.objects.values_list('calc')
    ]))
    predictions.decide_boundary(4, "Applied Physics", "AB/ap.png", np.array([
        *models.GradesA.objects.values_list('ap'),
        *models.GradesB.objects.values_list('ap')
    ]))
    predictions.decide_boundary(4, "Applied Physics", "C/ap.png", np.array([
        *models.GradesC.objects.values_list('ap')
    ]))
    predictions.decide_boundary(4, "DLD", "AB/dld.png", np.array([
        *models.GradesA.objects.values_list('dld'),
        *models.GradesB.objects.values_list('dld')
    ]))
    predictions.decide_boundary(4, "DLD", "C/dld.png", np.array([
        *models.GradesC.objects.values_list('dld')
    ]))
    predictions.decide_boundary(4, "OOP", "AB/oop.png", np.array([
        *models.GradesA.objects.values_list('oop'),
        *models.GradesB.objects.values_list('oop')
    ]))
    predictions.decide_boundary(4, "OOP", "C/oop.png", np.array([
        *models.GradesC.objects.values_list('oop')
    ]))
    return True


def process_form(request):
    input_data = request.POST
    if input_data['section'].upper() not in ['A', 'B', 'C'] or input_data['id'][-12:] != ".bscs21seecs":
        return render(request, "invalid.html")

    # Check For Username in DB
    try:
        obj = tables[input_data['section'].upper()].objects.get(uname=input_data["id"])
        if obj.password != input_data["password"]:
            return render(request, "invalid.html")
    except Exception as e:
        # Check on NUST Record
        if add_new_record(input_data):
            obj = tables[input_data['section'].upper()].objects.get(uname=input_data["id"])
        else:
            return render(request, "invalid.html")

    aggregates = {"aggAP": obj.ap, "aggCAL": obj.calc, "aggDLD": obj.dld, "aggOOP": obj.oop,
                  "aggISL": obj.istd, "aggITM": obj.imgt}
    context = {"name": obj.name, "uname": input_data["id"], "section": input_data["section"], **aggregates}

    sequence = {"grAP": "ap", "grCAL": "calc", "grDLD": "dld", "grOOP": "oop", "grISL": "istd", "grITM": "imgt"}
    for k, v in sequence.items():
        if v in ["ap", "dld", "oop"]:
            if input_data['section'].upper() == "C":
                data = np.array([*models.GradesC.objects.values_list(v)])
            else:
                data = np.array([*models.GradesA.objects.values_list(v),
                                 *models.GradesB.objects.values_list(v)])
        else:
            data = np.array([*models.GradesA.objects.values_list(v),
                             *models.GradesB.objects.values_list(v),
                             *models.GradesC.objects.values_list(v)])
        if v in ["ap", "oop", "dld"]:
            ch = 4
        elif v in ["istd", "imgt"]:
            ch = 2
        else:
            ch = 3
        context[k], context[k.replace('gr', 'p')], context[k.replace('gr', 'pd')] = predictions.make_prediction(aggregates[k.replace('gr', 'agg')], ch, data)
    return render(request, "result.html", context)


def index(request):
    if request.POST.get('id'):
        return process_form(request)
    return render(request, "login.html")
