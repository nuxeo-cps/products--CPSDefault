// $Id$
// this script make rss link clickable and add a validator link

var xlink = "http://www.w3.org/1999/xlink";
var allItems = document.getElementsByTagName("item");
for (var i=0;i<allItems.length;i++)
{
    var itemElm = allItems[i];
    var linkElm = itemElm.getElementsByTagName("link").item(0);
    var linkURL = linkElm.firstChild.nodeValue;

    linkElm.setAttributeNS(xlink,"type","simple");
    linkElm.setAttributeNS(xlink,"show","replace");
    linkElm.setAttributeNS(xlink,"href", linkURL);
}

var channelElm = document.getElementsByTagName("channel").item(0);
var linkElm = channelElm.getElementsByTagName("link").item(0)
var feedURL = linkElm.firstChild.nodeValue;

validatorElm = document.createElementNS(xlink, "link");
validatorElm.setAttribute("id","validatorRSS");
validatorElm.setAttributeNS(xlink,"type","simple");
validatorElm.setAttributeNS(xlink,"show","replace");
validatorElm.setAttributeNS(xlink,"href","http://feedvalidator.org/check.cgi?url=" + feedURL);
textNode = document.createTextNode("Validate this RSS feed")
validatorElm.appendChild(textNode)
document.lastChild.appendChild(validatorElm);
