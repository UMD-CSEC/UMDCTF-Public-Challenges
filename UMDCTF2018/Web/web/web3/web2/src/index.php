<html>
	<head>
		<title>Internet of Lumpus</title>
	</head>
	<body>
	<h1>Lumpus' Internet of Things Control Panel</h1>
	<img width="200" height="200" src="https://yt3.ggpht.com/a-/AJLlDp3onUsLAvOnzZW_rcPCiRJbdLqIayO7nD3X2w=s900-mo-c-c0xffffffff-rj-k-no">
	<h3>Written in PHP so it is very secure - hackers stay away</h3>
	<form method="get">

		<select name="device">
			<option value="thermostat.php">Thermostat</option>
			<option value="webcam.php">IP Webcam</option>
			<option value="atm.php">Portable ATM</option>
		</select>
		<input type="submit">
	</form>
	
	<br />
	<?php
	   if ( isset( $_GET['device'] ))  {
	      echo "<h2>Status:</h2> <br />";
	      include( $_GET['device']  );
	   }
	?>
	</body>
</html>
