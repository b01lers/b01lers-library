<?php
if (isset($_GET['src'])) {
    highlight_file("index.php");
    die();
}

if ($_SERVER['REQUEST_METHOD'] === 'GET' && isset($_GET['key1']) && isset($_GET['key2'])) {
    if ($_GET['key1'] == $_GET['key2']) {
        die("key1 and key2 must be different!");
    } else if (md5($_GET['key1']) == md5($_GET['key2'])) {
        echo "Correct!\n";
        echo file_get_contents("/flag.txt");
        die();
    } else {
        die("Hashes don't match!");
    }
}
?>
<html>
    <body>
      <p>Your job is simple. Give me 2 different inputs that hash (sha256) to the same value.</p>
      <form method="GET">
        <input type="text" name="key1" placeholder="Key 1" /><br/>
        <input type="text" name="key2" placeholder="Key 2" /><br/>
        <input type="submit" value="Submit" />
      </form>
      <br><br>
      <form method="GET">
        <input hidden type="text" name="src" value="src" />
        <input type="submit" value="See source" />
      </form>
    </body>
</html>
