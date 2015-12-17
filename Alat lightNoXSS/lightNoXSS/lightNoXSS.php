<?php

if (!empty($_REQUEST)){
    $num=0;
    //za testne svrhe dodati noPro polje u zahtjev pa se ne izvršava obrana
    //TREBA UKLONITI "if" KADA SE POČNE KORISTITI NA STRANICI KOJA JE U POGONU
    //odkomentirati "if" z testne svrhe
    //if (!isset($_REQUEST["noPro"]) || $_REQUEST["noPro"]!="on")
        $num=clean();

    //log datoteka gdje se zapisuje broj napada na stranicu kada se detektiraju
    if ($num>0){
        $timeDate=getdate();
        $log=fopen("lightNoXSS/napadi.log","a");
        $zapis="";
        $zapis=$_SERVER['REMOTE_ADDR']."\t".$timeDate["mday"].".".$timeDate["mon"].".".$timeDate["year"]."\t";
        $zapis.=$timeDate["hours"].":".$timeDate["minutes"].":".$timeDate["seconds"]."\t";
        $zapis.=$_SERVER["HTTP_REFERER"]."\t".strval($num)." napada".PHP_EOL;
        fwrite($log, $zapis);
        fclose($log);
     }
}

function clean(){
    //dohvatiti JSON s filterima i parsirati ga
    $json = file_get_contents("lightNoXSS/filteri.json");
    $objekt = json_decode($json,true);
    
    //do svakog pravila se pristupa kao: $objekt['filters']['filter'][<ID>]['rule']
    //gdje je <ID> redni broj pravila počevši od 0
    //jer je tako u JSON organiziran
    $opasnost=false;
    $k="";
    $num=0;
    foreach ($_REQUEST as $k => $v){
        foreach ($objekt["filters"]["filter"] as $val){
            if ( preg_match("/".$val["rule"]."/",$v) ){
                $_REQUEST[$k]=htmlentities($v,ENT_QUOTES,"UTF-8");
                //pamti opasni string i njegov ključ u polju $_REQUEST
                $opasnost=true;
                $key=$k;
                $num+=1;
                break(1);
            }
        }
    }

    return $num;
}
             //     <listing>&ltimg src=x onerror=alert(1)&gt</listing>
?>

<script src="/lightNoXSS/script/NOmXSS.js"></script>