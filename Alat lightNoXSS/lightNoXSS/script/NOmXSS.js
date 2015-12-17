/*
    Ova je skripta preuzeta sa http://html5sec.org/trueHTML
    uz dopuštenje autora. Autor je Mario Heiderich, http://mario.heideri.ch
    Načinjeno je nešto preinaka na istoj. Originalna se može naći na:
    http://html5sec.org/trueHTML/trueHTML.js
    Pod MPL licencom je.
*/

var changeHandler = function(element, type){
        var serializer = new XMLSerializer();
        var domstring = '';
        if(type === 'outerHTML') {
            try {
                domstring += serializer.serializeToString(element);
            } catch(e) {}
        } else {
            for(var i in element.childNodes) {
                try {
                    domstring += serializer.serializeToString(element.childNodes[i]);
                } catch(e) {}
            }
        }
        return domstring;
}

function NOmXSS(element){
    if(typeof element.innerHTML === 'string') {
        return changeHandler(this, 'innerHTML');
    }
    if(typeof element.outerHTML === 'string') {
        return changeHandler(this, 'outerHTML');
    }
}