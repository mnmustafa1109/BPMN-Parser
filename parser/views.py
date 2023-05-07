from django.views.generic import TemplateView
from django.shortcuts import render,redirect
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
       contents =f.read()
    return contents


def result(request):
    
    #return error if file is not present
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
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}messageFlow":
                flows.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}association":
                flows.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}dataAssociation":
                flows.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}dataInputAssociation":
                flows.append(child)
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}dataOutputAssociation":
                flows.append(child)
            



    template_name = "index.html"
    
    # store name of the lanes, tasks, events and processes in a list
    
    lanes_name = []
    
    for lane in lanelist:
        lanes_name.append(lane.attrib['name'])
        
    task_data = {}
    total_time = 0
    
        # go into extensionElements tag
    for task in tasks:
        for child in task:    
            if child.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}extensionElements":
                for child2 in child:
                    if child2.tag == "{http://camunda.org/schema/zeebe/1.0}properties":
                        print(child2.tag)
                        for child3 in child2:
                            if child3.tag == "{http://camunda.org/schema/zeebe/1.0}property":
                                    # get the Time property 
                                if child3.attrib['name'] == "Time":
                                    task_data[task.attrib['name']] = child3.attrib['value']
                                    total_time += int(child3.attrib['value'])

        
    events_name = []
    
    for event in events:
        events_name.append(event.attrib['name'])
        
    processes_name = []
    
    for process in processlist:
        processes_name.append(process.attrib['name'])
        
    gateways_name = []
    
    for gateway in gateways:
        gateways_name.append(gateway.attrib['name'])
        

    # remove file
    # if os.path.isfile("static/upload/bpmn.xml"):
        # os.remove("static/upload/bpmn.xml")
    
    # display the numbers of lanes, tasks, events and processes
    return render(request, template_name, {'lanes': lanes_name, 'tasks': task_data, 'events': events_name, 'processes': processes_name, 'gateways': gateways_name, 'flows': flows, 'total_time': total_time})

    
    
# upload file
def upload(request,error = None):
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
    