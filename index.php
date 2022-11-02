<?php
error_reporting(E_ALL);
// session_set_cookie_params(2*60*60, '/', 'votresite.binets.fr', true, true);
session_start();

$files = glob('classes/*.php');
foreach ($files as $file) {
    require($file);
}

$conn = Database::connect();

$page_info = PageListing::getCurrent();
//name, title, connected, root
extract($page_info);
?>

<!DOCTYPE html>
<html lang="fr">
    
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title><?= $title ?></title>
        <?php require("includes/linksAndScripts.php") ?>
    </head>
    
    <body>
        <div class="mainContent">
            <?php
            PageListing::load($page_info);
        ?>
    </div>
    <?php
    require("includes/footer.php")
    ?>
</body>

</html>