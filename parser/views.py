from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.files import File
from django.core.files.storage import FileSystemStorage
import xml.etree.ElementTree as ET
import os
from . import forms

xmlpath = "static/upload/bpmn.xml"


def readfile(request):
    f = open(xmlpath, "r")
    if f.mode == 'r':
        contents = f.read()
    return contents


def result(request):
    # return error if file is not present
    if not os.path.exists(xmlpath):
        return upload(request, error="File not found")

    myroot = ET.fromstring(readfile(request))

    lanelist = []
    processlist = []
    events = []
    tasks = []
    gateways = []
    flows = []

    # go into bpmn:definitions child 
    for child in myroot:
        # find number of bpmn:process child
        if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}process":
            # save the all process child in a list
            processlist.append(child)

    for process in processlist:
        for child in process:
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}laneSet":
                laneSet = child
                for lane in laneSet:
                    lanelist.append(lane)

    for process in processlist:
        for child in process:
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}startEvent":
                events.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}endEvent":
                events.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}intermediateCatchEvent":
                events.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}intermediateThrowEvent":
                events.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}boundaryEvent":
                events.append(child)

    for process in processlist:
        for child in process:
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}task":
                tasks.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}userTask":
                tasks.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}serviceTask":
                tasks.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}scriptTask":
                tasks.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}businessRuleTask":
                tasks.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}sendTask":
                tasks.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}receiveTask":
                tasks.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}manualTask":
                tasks.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}callActivity":
                tasks.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}subProcess":
                tasks.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}transaction":
                tasks.append(child)

    for process in processlist:
        for child in process:
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}exclusiveGateway":
                gateways.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}inclusiveGateway":
                gateways.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}parallelGateway":
                gateways.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}eventBasedGateway":
                gateways.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}complexGateway":
                gateways.append(child)

    for process in processlist:
        for child in process:
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}sequenceFlow":
                flows.append(child)

    template_name = "index.html"

    processes_data = {}

    for process in processlist:
        processes_data[process.attrib['name']] = 0

    # store name of the lanes, tasks, events and processes in a list

    lanes_data = {}

    for lane in lanelist:
        lanes_data[lane.attrib['name']] = 0

    task_data = {}
    total_time = 0

    event_data = {}

    cycle_time = 0.0

    # go into extensionElements tag
    for task in tasks:
        for child in task:
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}extensionElements":
                for child2 in child:
                    if child2.tag == "{http://camunda.org/schema/zeebe/1.0}properties":
                        current_time = 0.0
                        current_probability = 1.0
                        for child3 in child2:
                            if child3.tag == "{http://camunda.org/schema/zeebe/1.0}property":
                                # check if it have a Probability property
                                if child3.attrib['name'] == "Probability":
                                    current_probability = float(child3.attrib['value'])
                                # get the Time property 
                                if child3.attrib['name'] == "Time":
                                    task_data[task.attrib['name']] = child3.attrib['value']
                                    total_time += int(child3.attrib['value'])
                                    current_time = int(child3.attrib['value'])
                                    # check if the task is in a lane
                                    for lane in lanelist:
                                        for child4 in lane:
                                            if child4.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}flowNodeRef":
                                                if child4.text == task.attrib['id']:
                                                    lanes_data[lane.attrib['name']] += int(child3.attrib['value'])
                                    # check if the task is in a process
                                    for process in processlist:
                                        for child4 in process:
                                            if child4.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}task":
                                                if child4.attrib['id'] == task.attrib['id']:
                                                    processes_data[process.attrib['name']] += int(
                                                        child3.attrib['value'])
                        cycle_time += current_time * current_probability

    print("Total time: " + str(total_time))

    for event in events:
        event_data[event.attrib['name']] = 0
        for child in event:
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}extensionElements":
                for child2 in child:
                    if child2.tag == "{http://camunda.org/schema/zeebe/1.0}properties":
                        current_time = 0.0
                        current_probability = 1.0
                        for child3 in child2:
                            if child3.tag == "{http://camunda.org/schema/zeebe/1.0}property":
                                # check if it have a Probability property
                                if child3.attrib['name'] == "Probability":
                                    current_probability = float(child3.attrib['value'])
                                # get the Time property 
                                if child3.attrib['name'] == "Time":
                                    event_data[event.attrib['name']] = child3.attrib['value']
                                    current_time = int(child3.attrib['value'])
                                    total_time += int(child3.attrib['value'])
                                    # check if the task is in a lane
                                    for lane in lanelist:
                                        for child4 in lane:
                                            if child4.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}flowNodeRef":
                                                if child4.text == event.attrib['id']:
                                                    lanes_data[lane.attrib['name']] += int(child3.attrib['value'])
                                    # check if the task is in a process
                                    for process in processlist:
                                        for child4 in process:
                                            if child4.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}event":
                                                if child4.attrib['id'] == event.attrib['id']:
                                                    processes_data[process.attrib['name']] += int(
                                                        child3.attrib['value'])
                        cycle_time += current_time * current_probability

    gateways_name = []

    for gateway in gateways:
        gateways_name.append(gateway.attrib['name'])

    sum_events = 0
    sum_tasks = 0
    sum_lanes = 0
    sum_processes = 0

    for event in event_data:
        sum_events += int(event_data[event])

    for task in task_data:
        sum_tasks += int(task_data[task])

    for lane in lanes_data:
        sum_lanes += int(lanes_data[lane])

    for process in processes_data:
        sum_processes += int(processes_data[process])

    # remove file
    # if os.path.isfile("static/upload/bpmn.xml"):
    # os.remove("static/upload/bpmn.xml")

    # display the numbers of lanes, tasks, events and processes
    return render(request, template_name,
                  {'lanes': lanes_data, 'tasks': task_data, 'events': event_data, 'processes': processes_data,
                   'gateways': gateways_name, 'flows': flows, 'total_time': total_time, 'sum_events': sum_events,
                   'sum_tasks': sum_tasks, 'sum_lanes': sum_lanes, 'sum_processes': sum_processes,
                   'cycle_time': cycle_time})


# upload file
def upload(request, error=None):
    template_name = "upload.html"
    if request.method == "POST":
        form = forms.UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            fs = FileSystemStorage()
            # delete the old file if present
            if os.path.isfile("static/upload/bpmn.xml"):
                os.remove("static/upload/bpmn.xml")
            filename = fs.save("static/upload/bpmn.xml", request.FILES['file'])
            uploaded_file_url = fs.url(filename)
            return redirect('result')


    else:
        form = forms.UploadFileForm()

    return render(request, template_name, {'form': form, 'error': error})
