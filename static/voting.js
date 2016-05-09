var likes = 0;
var no = 0;

function IncreaseLikes()
{
    likes++;
    document.getElementById("likes").innerHTML = likes;
}

function decreaseLikes()
{
    no--;
    document.getElementById("no").innerHTML = no;
}