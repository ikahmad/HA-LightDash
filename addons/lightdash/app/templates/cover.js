<script>
document.addEventListener("DOMContentLoaded",function(){
var m=document.getElementById("cover-modal");
var track=document.getElementById("cover-track");
var fill=document.getElementById("cover-fill");
var posEl=document.getElementById("cover-pos");
var nameEl=document.getElementById("cover-name");
var closeBtn=document.getElementById("cover-close-btn");
var upBtn=document.getElementById("cover-btn-up");
var stopBtn=document.getElementById("cover-btn-stop");
var downBtn=document.getElementById("cover-btn-down");
var _curEid="",_curPos=0;
var _lpTimer=null,_acTimer=null;

function setPos(v){
v=Math.max(0,Math.min(100,Math.round(v)));
_curPos=v;
posEl.textContent=v+"%";
fill.style.height=v+"%";
var p=v/100;
var r=Math.round(120+120*p);
var g=Math.round(180+30*p);
var b=Math.round(200-80*p);
fill.style.background="rgb("+r+","+g+","+b+")";
}

function sendPos(){
if(!_curEid)return;
navigator.sendBeacon("$action_url",JSON.stringify({entity_id:_curEid,action:"call-service",service:"cover.set_cover_position",data:{position:_curPos}}));
}

function doCoverAction(svc){
if(!_curEid)return;
navigator.sendBeacon("$action_url",JSON.stringify({entity_id:_curEid,action:"call-service",service:svc}));
}

function showCover(eid,ename,epos,favVals){
_curEid=eid;
nameEl.textContent=ename||"";
var p=epos!==null&&epos!==undefined?Math.max(0,Math.min(100,Math.round(epos))):50;
setPos(p);
$auto_close_timer
m.style.display="";
var leftEl=document.getElementById("cover-left");
if(leftEl){leftEl.innerHTML="";if(favVals){favVals.split(",").forEach(function(v){var btn=document.createElement("button");btn.textContent=v+"%";btn.className="cover-fav-btn";btn.addEventListener("click",function(){setPos(parseInt(v));sendPos();$auto_close_reset});leftEl.appendChild(btn)})}}
}

function hideCover(){m.style.display="none";_curEid=""}

closeBtn.addEventListener("click",function(){$auto_close_resethideCover()});
m.addEventListener("click",function(e){if(e.target===m){$auto_close_resethideCover()}});
upBtn.addEventListener("click",function(){doCoverAction("cover.open_cover");setPos(100)});
stopBtn.addEventListener("click",function(){doCoverAction("cover.stop_cover")});
downBtn.addEventListener("click",function(){doCoverAction("cover.close_cover");setPos(0)});

var _drag=false;
function dragY(y){
var rect=track.getBoundingClientRect();
var v=Math.round((1-(y-rect.top)/rect.height)*100);
setPos(v);
}

track.addEventListener("touchstart",function(e){_drag=true;dragY(e.touches[0].clientY);$auto_close_reset},true);
track.addEventListener("touchmove",function(e){if(_drag){e.preventDefault();dragY(e.touches[0].clientY)}},true);
track.addEventListener("touchend",function(e){if(_drag){_drag=false;sendPos();$auto_close_reset}},true);
track.addEventListener("mousedown",function(e){_drag=true;dragY(e.clientY);$auto_close_reset},true);
document.addEventListener("mousemove",function(e){if(_drag){e.preventDefault();dragY(e.clientY)}},true);
document.addEventListener("mouseup",function(e){if(_drag){_drag=false;sendPos();$auto_close_reset}},true);

document.addEventListener("touchstart",function(e){
var row=e.target.closest(".tile-card[data-cover-entity],.entity-row[data-cover-entity]");
if(!row)return;
var eid=row.getAttribute("data-cover-entity");
var favVals=row.getAttribute("data-fav-vals")||"";
_lpTimer=setTimeout(function(){
var ename=(row.querySelector(".tile-name")||row.querySelector(".entity-name")||{}).textContent||"";
fetch("$state_api_url"+encodeURIComponent(eid)).then(function(r){return r.json()}).then(function(d){
if(d&&!d.error){
var epos=(d.attributes&&d.attributes.current_position);
showCover(eid,ename,epos,favVals);
}else{
showCover(eid,ename,50,favVals);
}
}).catch(function(){showCover(eid,ename,50,favVals)});

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
var row=e.target.closest(".tile-card[data-cover-entity],.entity-row[data-cover-entity]");
if(!row)return;
var eid=row.getAttribute("data-cover-entity");
var favVals=row.getAttribute("data-fav-vals")||"";
_lpTimer=setTimeout(function(){
var ename=(row.querySelector(".tile-name")||row.querySelector(".entity-name")||{}).textContent||"";
fetch("$state_api_url"+encodeURIComponent(eid)).then(function(r){return r.json()}).then(function(d){
if(d&&!d.error){
var epos=(d.attributes&&d.attributes.current_position);
showCover(eid,ename,epos,favVals);
}else{
showCover(eid,ename,50,favVals);
}
}).catch(function(){showCover(eid,ename,50,favVals)});

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
