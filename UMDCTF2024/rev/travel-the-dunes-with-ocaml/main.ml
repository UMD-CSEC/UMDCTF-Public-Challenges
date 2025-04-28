let flag = [85; 77; 68; 67; 84; 70; 123; 114; 118; 103; 120; 98; 118; 104; 109; 56; 57; 116; 99; 56; 51; 111; 99; 51; 116; 56; 52; 109; 111; 57; 48; 109; 56; 51; 100; 116; 52; 109; 95; 95; 95; 95; 95; 115; 51; 82; 49; 48; 85; 115; 49; 89; 95; 119; 104; 79; 95; 64; 99; 116; 117; 64; 49; 49; 121; 95; 117; 115; 69; 115; 95; 48; 99; 64; 109; 49; 63; 63; 63; 95; 95; 95; 95; 95; 97; 108; 55; 111; 102; 51; 55; 100; 51; 111; 116; 100; 120; 108; 115; 100; 116; 56; 110; 121; 115; 102; 108; 110; 56; 121; 52; 51; 102; 115; 103; 55; 120; 117; 118; 110; 115; 102; 125];;
let flag_len = 123;;

Printf.printf "===============================================\n";;
Printf.printf "OCaml Flag Checker (v 1.0.0)\n";;
Printf.printf "===============================================\n";;

Printf.printf "Make a guess: \n";;
flush stdout;;

let user_input = input_line stdin;;

let rec check_input s i =
  if (i < flag_len) then
    let chr = s.[i] in
    let user_ascii = Char.code chr in
    let correct_ascii = List.nth flag i in

    Printf.printf "Checking: %c" chr;

    if (user_ascii != correct_ascii) then begin
      Printf.printf " - Incorrect Match! Terminating program...\n";
      flush stdout;
      exit 1;
    end
    else begin
      Printf.printf " - Match!\n";
      flush stdout;
    end;

    check_input s (i + 1);  (* Recursive call for the next character *)
in

if (String.length user_input != flag_len) then begin
  Printf.printf "Incorrect length!\n";
  flush stdout;
  exit 1;
end
else
  check_input user_input 0;
  Printf.printf "Checking completed.\n";
  flush stdout;
  exit 0;
