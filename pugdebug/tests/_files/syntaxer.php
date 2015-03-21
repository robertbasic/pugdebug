<?php
/**
 * This PHP file is for testing the syntaxer
 *
 * PHP files start with a <?php and end with a ?>
 *
 * PHP files use $variables
 */

// Comment with a $variable

$variable = null; // this $variable has a null value

$camel_case = $upperCase = 2;

$array = [
    'foo' => 'bar\'s value'
];

class Foo {
    private $x = 0;
    protected $y = 'a';
    public $z = null;

    public function stuff()
    {
        return array_flip(array_combine(range(1,10), range(10,1)));
    }
}

$foo = new Foo();
?>

this $var is outside * <?php echo 'inline'; ?>

<a href='#'><?php echo 'inline php'; ?></a>

skip this line $completely

<?php // more than one php block in a file ?>
