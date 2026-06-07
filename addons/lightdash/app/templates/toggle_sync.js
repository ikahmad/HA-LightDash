<script>
var sau="$state_api_url";
function st(){
document.querySelectorAll(".tile-card").forEach(function(e){
var s=e.querySelector(".entity-state"),t=e.querySelector(".toggle-input");
if(s){var o=s.textContent.trim()==="on";if(t)t.checked=o;e.classList.toggle("entity-on",o);e.classList.toggle("entity-off",!o);}
});
document.querySelectorAll(".entities-card .entity-row").forEach(function(e){
var s=e.querySelector(".entity-state"),t=e.querySelector(".toggle-input");
if(s){var o=s.textContent.trim()==="on";if(t)t.checked=o;e.classList.toggle("entity-on",o);e.classList.toggle("entity-off",!o);}
});}
function uc(s){
var t0=s.textContent.trim().toLowerCase();
var c=s.closest(".tile-card,.entity-row,.glance-item,.button-card,button");
if(!c||(t0!=="on"&&t0!=="off"))return;
var p=t0==="off"?0:+s.style.getPropertyValue("--b")||100;
p=Math.max(0,Math.min(100,p));
var r=Math.round(221+25*p/100),g=Math.round(221-26*p/100),b=Math.round(221-153*p/100);
var clr="#"+((1<<24)+(r<<16)+(g<<8)+b).toString(16).slice(1);
if(c.classList.contains("tile-card"))c.style.setProperty("--tile-color",clr);
else c.style.setProperty("--state-color",clr);
}
 document.addEventListener("DOMContentLoaded",function(){st();document.querySelectorAll(".entity-state").forEach(uc);});
 document.addEventListener("htmx:afterSwap",function(){st();document.querySelectorAll(".entity-state").forEach(uc);});
  document.addEventListener("htmx:sseMessage",function(e){
  st();
  var s=e.target;
  if(!s||!s.classList.contains("entity-state"))return;
 var eid=s.getAttribute("data-entity");
 if(eid&&s.getAttribute("data-brightness")){
 fetch(sau+eid).then(function(r){return r.json()}).then(function(d){
 if(d&&d.attributes&&d.attributes.brightness){
 var p=Math.round(d.attributes.brightness/255*100);
 s.style.setProperty("--b",p);
 s.setAttribute("data-brightness",d.attributes.brightness);}
 uc(s);});
 }else{uc(s);}
 });
  document.addEventListener("change",function(e){
  var i=e.target;
  if(!i.classList.contains("toggle-input"))return;
  var on=i.checked;
  var c=i.closest(".tile-card,.entity-row");
  if(c){c.classList.toggle("entity-on",on);c.classList.toggle("entity-off",!on);}
  var s=c&&c.querySelector(".entity-state");
  if(s){var t0=s.textContent.trim().toLowerCase();if(t0==="on"||t0==="off")s.textContent=on?"on":"off";uc(s);}
  });
  document.addEventListener("click",function(e){
  var c=e.target.closest(".tile-card,.entity-row");
  if(!c)return;
  if(e.target.closest("button,a,input,select,textarea,.toggle-switch,.entity-toggle"))return;
   var s=c.querySelector(".entity-state"),t=c.querySelector(".toggle-input");
   if(!s)return;
  var x=s.textContent.trim().toLowerCase();
  if(x!=="on"&&x!=="off")return;
  var on=x==="on"?false:true;
  s.textContent=on?"on":"off";
   if(t)t.checked=on;
  c.classList.toggle("entity-on",on);
  c.classList.toggle("entity-off",!on);
  uc(s);
  });
</script>
