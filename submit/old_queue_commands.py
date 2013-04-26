#!/usr/bin/env python
# Purpose: Submit a job to the queue. This function is highly platform-specific and may need to be modified.
# Authors: Tam Mayeshiba
# 10/25/12 TTM created
# 12/6/12 TTM added UKY DLX commands
import os
import sys

system = "bardeen" #dlx, curie, bardeen, nersc, ranger
compute_node = True
def submit_command(runpath, scriptname):
    """
        Get the text to submit a job to the queue.
        INPUTS:
            runpath <str> = full path of the run to submit
            scriptname <str> = name (with extension) of the submission script (ex: submit.sh)
        OUTPUTS:
            <str> = text to run in the shell
    """
    selfstr=""
    if(compute_node): 
        if system == "ranger":####Ranger, from compute node
            selfstr="ssh -f ranger 'cd " + runpath + "; qsub " + scriptname + "'"
        if system == "bardeen": ####Bardeen, from compute node
            selfstr="ssh -f bardeen 'cd " + runpath + "; qsub " + scriptname + "'"
        if system == "curie": ####Curie, from compute node
            selfstr="ssh -f curie 'cd " + runpath + "; qsub " + scriptname + "'"
    else:###Direct test, from headnode
        selfstr="qsub " + scriptname
        if system == "dlx":###University of Kentucky DLX machine, direct test from headnode
            selfstr="sbatch " + scriptname
    return selfstr


def queue_status_from_text(jobid, queuetext):
    """
        Returns the queue status from a line with the job ID information
        INPUTS:
            jobid <int> = job ID
            qstr <str> = queue snapshot line containing job ID
        OUTPUTS:
            <str> = queue status 
            'E': Error
            'X': Not found
            'R': Running
            'W': Waiting
    """
    if (queuetext == None): 
        return 'X'
    if len(queuetext) == 0:
        return 'X'
    begin = queuetext.find(str(jobid))
    if begin == -1:
        return 'X'
    queuetext = queuetext[begin:]
    end = queuetext.find('\n')
    if end > -1:
        queuetext = queuetext[:end]

    if system == "ranger":####Ranger
        ranger_out = queuetext.split()[4]
        if (ranger_out == 'wq') or (ranger_out == 'qw'):
            final_out = 'Q'
        elif ranger_out == 'r':
            final_out = 'R'
        return final_out

    if system == "bardeen" or system == "curie":###Bardeen, Curie, etc.
        qmat = queuetext.split()
        if len(qmat) < 5:
            return 'E'
        return qmat[4] #TTM 1/17/12 qstat returns differently than qstat -a does
    
    if system == "dlx":####UKy DLX
        queuetext = queuetext.strip()
        dlx_out = queuetext.split()[4] #indexing starts at 0
        if (dlx_out == 'PD'):
            final_out = 'Q'
        elif dlx_out in ['CG','CD','R']:
            final_out = 'R'
        return final_out

def extract_submitted_jobid(string):
    """
        Extract the job ID from a string returned when the job is submitted
        INPUTS:
            string <str> = string with job ID somewhere in it
        OUTPUTS:
            <int> = job ID as integer
    """
    ####Bardeen and Curie:
    if system == "bardeen" or system == "curie":
        final = ""
        for char in string:
            if(char != '.'):
                final += char
            else:
                return int(final)

    if system == "ranger":####Ranger:
        findme=0
        findstr=""
        findme = string.find("Your job") # ..... Your job 12345678 has been submitted.
        if findme == -1: #TTM+1 2/11/12 if not found, return negative 1
            return -1
        findstr = string[findme+9:]
        splitstr=[]
        splitstr = findstr.split()
        return int(splitstr[0])

    if system == "dlx":###UKY DLX:
        findstr = string.strip()
        return int(findstr.split()[3])

def queue_snap_command():
    """
        Return the command for producing a queue snapshot.
        INPUTS:
            None
        OUTPUTS:
            Command for producing a queue snapshot
    """
    qcmd=""
    if(compute_node):
        if(system == "ranger"):####Ranger, from compute node
            #
            qcmd = "ssh -f ranger 'qstat'"

        if(system == "bardeen"):####Bardeen, from compute node
            qcmd = "ssh -f bardeen 'qstat'" 
    
        if(system == "curie"):####Curie, from compute node
            qcmd = "ssh -f curie 'qstat'"
    else:###Direct from headnode
        qcmd = 'qstat 2> /dev/null' #TTM 052212 sometimes requires /bin/bash
    ###Direct from headnode, UKY DLX:
        if(system == "dlx"):
            uname=os.getenv("USER")
            qcmd = "squeue -u " + uname
    return qcmd

