<!DOCTYPE html>
<html lang="en">
<head>
  <title>Sign In</title>
  <meta charset="utf-8">
  <link rel="stylesheet" href="css/home.css">
</head>
<body>

<form method="post">
    <p>Username:</p>
    <input type="text" name="username" id="unameinput"/>
    <p>Password:</p>
    <input type="password" name="password" id="pwordinput"/><br/>
    <input type="submit" name="test" id="test" value="RUN" />
</form>

<?php
    function testfun(){
        $servername = getenv('IP');
        $username = 'connected';
        $password = 'secure';
        $database = "c9";
        $dbport = 3306;
        $db = new mysqli($servername, $username, $password, $database, $dbport);
        
        $username = str_replace('"', '', $_POST['username']);
        $username = str_replace("'", '', $username);
        $password = str_replace('"', '', $_POST['password']);
        $password = str_replace("'", '', $password);
        $password = str_ireplace("or", '', $password);
        
        $result = $db->query("SELECT * FROM users WHERE username='" . $username . "' AND password='" . $password ."'");
        
        if (!$result) {throw new Exception("Database Error");}
        
        else{while($row = $result->fetch_assoc()){
                echo $row["username"] . " " . $row["password"] . "<br>";
            }}
    }
    
    if(array_key_exists('test', $_POST)){testfun();}

?>

</body>
</html>

