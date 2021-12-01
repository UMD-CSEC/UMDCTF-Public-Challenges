<?php 
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
$html = "";
$userAgent = $_SERVER['HTTP_USER_AGENT'];
if (strpos("sqlmap", $userAgent) === false) {
    if ($_SERVER['REQUEST_METHOD'] == "POST") {
        $link = mysqli_connect("db", "root", "UMD_CTF_DB_PW", "umdctf");
        $filter =  "/[A-Za-z0-9%]+/";
        $result = false;
        $badWordFound = false;
        $message = "";
        $authenticated = false; 
        $badwords = [];
        $badwords = ['or', 'and', 'not', 'union', 'select', 'insert', 'update'];
        $username = $_POST['username'];
        $password = $_POST['password'];
        for ($i = 0; $i < count($badwords); $i++) {
            if (strpos(strtolower($_POST['username']), $badwords[$i]) !== false || strpos(strtolower($_POST['password']), $badwords[$i]) !== false) {
            $badWordFound = true;
        }
        }
        if (!preg_match($filter, $_POST['username']) || !preg_match($filter, $_POST['password'])) {
            $badWordFound = true; 
        }
        if (!$badWordFound) {
    
            $query = "SELECT username, pass FROM users where username = '$username' and pass = '$password';";
            $result = mysqli_query($link, $query);
    
            if ($result && mysqli_num_rows($result) > 0) {
        
                while ($row = mysqli_fetch_assoc($result)) {
                    if ($username == $_POST['username']){
                $authenticated = true;    
                $username = $row['username'];
                        $password = $row['pass'];
                        $message = $message . "You have successfully logged in!</h1><br><h1>Account Details:</h1><br><h1>Username: " . $username . "</h1><br><h1>Password: " . $password;
                        } 
            }
            } else {
            $message = $message . "Unable to login";
            }
        } else {
            $message = $message . "Unable to login";	    
        }
    }
}

?>

<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'>
    <meta http-equiv='X-UA-Compatible' content='IE=edge'>
    <title>Page Title</title>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
    <link rel='stylesheet' type='text/css' media='screen' href='main.css'>
</head>
<body>
    <div class = "container-fluid">
    <?php if ($_SERVER['REQUEST_METHOD'] == "GET") { ?>
        <div class = "row">
            <div class = "col-12">
                <h1 class = "text-center">Houston Astros Sign Stealer Login</h1>
            </div>
        </div>
        <form method = "POST">

            <div class = "row">
                <div class = "col-12">
                    <input type = "text" class = "form-control" name = "username" placeholder = "Username">
                </div>
            </div>
            <div class = "row">
                <div class = "col-12">
                    <input type = "password" class = "form-control" name = "password" placeholder = "Password">   
                </div>
            </div>
            <br>
            <div class = "row">
                <div class = "col-12 text-center">
                    <input type="submit" value = "Submit" class = "btn btn-primary text-center" />
                </div>
            </div>
        </form>
        <br>
        <div class = "row">
            <div class = "col-12 text-center">
                <img class="logoSize" src="houston_asterisks.jpg" />
            </div>
        </div>
    <?php } else { ?>
        <div class = "row">
            <div class = "col-12 text-center">
                <h1><?php echo $message; ?></h1>
            </div>
       </div>
       <div class = "row">
            <div class = "col-12 text-center">
                <img class="signSize" src="catcher-signs.gif" />
            </div>
        </div>
    <?php } ?>
    </div>
    <script src="https://code.jquery.com/jquery-3.4.1.slim.min.js" integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>
</body>
</html>
