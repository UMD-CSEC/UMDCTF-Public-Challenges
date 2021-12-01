<?php 
$returnContents = [];
error_reporting(0);


if ($_SERVER['REQUEST_METHOD'] === "POST"){
    $regexpText = "/.*\.(txt)/i";
    $regexpImage = "/\.(gif|jpe?g|tiff|png|webp|bmp)$/i";
    $regexpTraversal = "/\.\./";
    $validFile = ['gif', 'txt',  'jpg', 'png'];
    if (isset($_POST['fileName'])) { 
	 
        $ext = substr($_POST['fileName'], -3, 3);
        $imageInServer = ['./files/homeplate.gif', './files/firstbase.jpg', './files/thirdbase.gif'];
        if (in_array($_POST['fileName'], $imageInServer) || $ext === "png" || $ext === "jpg" || $ext === "gif") {
            $returnContents['data'] = "<br><img class=\"text-center\" src=\"{$_POST['fileName']}\" height=\"600\" alt=\"File not found\" />"; 
        } else {
            $contents = file_get_contents($_POST['fileName']);
            if ($contents != false) {
                $contents = explode("\n", $contents);
                $returnContents['data'] = "<ul>";
                for ($i = 0; $i < sizeof($contents); $i++) {
                    $returnContents['data'] .= "<li>" . $contents[$i] . "</li>";
                }
                $returnContents['data'] .= "</ul>";
            } else {
                $returnContents['data'] = "File not found". $_POST['fileName'];
            }
        }
    }
}



?>

<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'>
    <meta http-equiv='X-UA-Compatible' content='IE=edge'>
    <title>L33t File Finder</title>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <link rel='stylesheet' type='text/css' media='screen' href='./style/main.css'>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
</head>
<body>
    <div class = "container">
        <div class = "row">
            <div class = "col-12">
                <h1 class = "text-center">Baseball Sign Stealing Software</h1>
            </div>
        </div>
        <form action="" method="POST">
            <div class = "row">
                <div class = "col-12">
                    <select name="fileName" class = "form-control">
                        <option value="">SELECT</option>
                        <option value="./files/homeplate.gif">Home Plate</option>
                        <option value="./files/firstbase.jpg">First Base</option>
                        <option value="./files/thirdbase.gif">Third Base</option>
                        <option value="./files/signs.txt">List of signs</option>
                    </select>                    
                </div>
            </div>
            <div class = "row">
                <div class = "col-12 text-center">
                    <br>
                    <input type = "submit" value = "Submit" class = "btn btn-success">
                </div>
            </div>
        </form>

        <div class = "row contents">
            <div class = "col-12 fileContents text-center">
                <?php 
                //if (isset($_GET['fileName'])) { 
                if ($_SERVER['REQUEST_METHOD'] === "POST") {
                    echo $returnContents['data']; 
                } ?>
            </div>
        </div>
    </div>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>
</body>
</html>
