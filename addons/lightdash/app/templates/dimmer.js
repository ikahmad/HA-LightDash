<script>
document.addEventListener("DOMContentLoaded",function(){
var m=document.getElementById("dimmer-modal");
var track=document.getElementById("dimmer-track");
var fill=document.getElementById("dimmer-fill");
var pct=document.getElementById("dimmer-pct");
var nameEl=document.getElementById("dimmer-name");
var closeBtn=document.getElementById("dimmer-close-btn");
var iconEl=document.getElementById("dimmer-icon");
var _curEid="",_curBri=0,_lastBri=100;
var _lpTimer=null,_acTimer=null;

function setBri(v){
v=Math.max(0,Math.min(100,Math.round(v)));
_curBri=v;
pct.textContent=v+"%";
fill.style.height=v+"%";
var r=Math.round(221-(221-246)*v/100);
var g=Math.round(221-(221-195)*v/100);
var b=Math.round(221-(221-68)*v/100);
fill.style.background="rgb("+r+","+g+","+b+")";
}

function sendBri(){
if(!_curEid)return;
navigator.sendBeacon("$action_url",JSON.stringify({entity_id:_curEid,action:"call-service",service:"light.turn_on",data:{brightness_pct:_curBri}}));
}

function showDimmer(eid,ename,ebri,isOn,iconSvg,favVals){
_curEid=eid;
nameEl.textContent=ename||"";
var b=isOn?Math.max(0,Math.min(100,Math.round((ebri||0)/255*100))):0;
if(isOn)_lastBri=b||100;
if(iconSvg){iconEl.innerHTML=iconSvg;iconEl.style.display=""}else{iconEl.innerHTML="";iconEl.style.display="none"}
setBri(b);
$auto_close_timer
m.style.display="";
var leftEl=document.getElementById("dimmer-left");
if(leftEl){leftEl.innerHTML="";if(favVals){favVals.split(",").forEach(function(v){var btn=document.createElement("button");btn.textContent=v+"%";btn.className="dimmer-fav-btn";btn.addEventListener("click",function(){setBri(parseInt(v));sendBri();$auto_close_reset});leftEl.appendChild(btn)})}}
}

function hideDimmer(){m.style.display="none";_curEid=""}

closeBtn.addEventListener("click",function(){${auto_close_reset}hideDimmer()});
m.addEventListener("click",function(e){if(e.target===m){${auto_close_reset}hideDimmer()}});

iconEl.addEventListener("click",function(){
if(!_curEid)return;
var isOn=_curBri>0;
if(isOn){
navigator.sendBeacon("$action_url",JSON.stringify({entity_id:_curEid,action:"call-service",service:"light.turn_off"}));
setBri(0);
}else{
var b=_lastBri||100;
navigator.sendBeacon("$action_url",JSON.stringify({entity_id:_curEid,action:"call-service",service:"light.turn_on",data:{brightness_pct:b}}));
setBri(b);
}
});

var _drag=false;
function dragY(y){
var rect=track.getBoundingClientRect();
var v=Math.round((1-(y-rect.top)/rect.height)*100);
setBri(v);
}

track.addEventListener("touchstart",function(e){_drag=true;dragY(e.touches[0].clientY);$auto_close_reset},true);
track.addEventListener("touchmove",function(e){if(_drag){e.preventDefault();dragY(e.touches[0].clientY)}},true);
track.addEventListener("touchend",function(e){if(_drag){_drag=false;sendBri();$auto_close_reset}},true);
track.addEventListener("mousedown",function(e){_drag=true;dragY(e.clientY);$auto_close_reset},true);
document.addEventListener("mousemove",function(e){if(_drag){e.preventDefault();dragY(e.clientY)}},true);
document.addEventListener("mouseup",function(e){if(_drag){_drag=false;sendBri();$auto_close_reset}},true);

document.addEventListener("touchstart",function(e){
var row=e.target.closest(".tile-card[data-light-entity],.entity-row[data-light-entity]");
if(!row)return;
var eid=row.getAttribute("data-light-entity");
var favVals=row.getAttribute("data-fav-vals")||"";
_lpTimer=setTimeout(function(){
var ename=(row.querySelector(".tile-name")||row.querySelector(".entity-name")||{}).textContent||"";
var iconEl2=row.querySelector(".tile-icon svg,.entity-icon svg");
var iconSvg=iconEl2?iconEl2.outerHTML:"";
fetch("$state_api_url"+encodeURIComponent(eid)).then(function(r){return r.json()}).then(function(d){
if(d&&!d.error){
var isOn=d.state==="on";
var ebri=(d.attributes&&d.attributes.brightness)||0;
showDimmer(eid,ename,ebri,isOn,iconSvg,favVals);
}else{
showDimmer(eid,ename,0,false,iconSvg,favVals);
}
}).catch(function(){showDimmer(eid,ename,0,false,iconSvg,favVals)});

var blocker=function(ev){ev.preventDefault();ev.stopPropagation();document.removeEventListener("click",blocker,true)};
document.addEventListener("click",blocker,true);
},500);
},true);

document.addEventListener("touchmove",function(e){
if(_lpTimer){clearTimeout(_lpTimer);_lpTimer=null}
},true);

document.addEventListener("touchend",function(e){
if(_lpTimer){clearTimeout(_lpTimer);_lpTimer=null}
},true);

document.addEventListener("mousedown",function(e){
var row=e.target.closest(".tile-card[data-light-entity],.entity-row[data-light-entity]");
if(!row)return;
var eid=row.getAttribute("data-light-entity");
var favVals=row.getAttribute("data-fav-vals")||"";
_lpTimer=setTimeout(function(){
var ename=(row.querySelector(".tile-name")||row.querySelector(".entity-name")||{}).textContent||"";
var iconEl2=row.querySelector(".tile-icon svg,.entity-icon svg");
var iconSvg=iconEl2?iconEl2.outerHTML:"";
fetch("$state_api_url"+encodeURIComponent(eid)).then(function(r){return r.json()}).then(function(d){
if(d&&!d.error){
var isOn=d.state==="on";
var ebri=(d.attributes&&d.attributes.brightness)||0;
showDimmer(eid,ename,ebri,isOn,iconSvg,favVals);
}else{
showDimmer(eid,ename,0,false,iconSvg,favVals);
}
}).catch(function(){showDimmer(eid,ename,0,false,iconSvg,favVals)});

var blocker=function(ev){ev.preventDefault();ev.stopPropagation();document.removeEventListener("click",blocker,true)};
document.addEventListener("click",blocker,true);
},500);
},true);

document.addEventListener("mousemove",function(e){
if(_lpTimer){clearTimeout(_lpTimer);_lpTimer=null}
},true);

document.addEventListener("mouseup",function(e){
if(_lpTimer){clearTimeout(_lpTimer);_lpTimer=null}
},true);

});
</script>
