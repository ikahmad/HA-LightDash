<script>
(function(){
function _initAlarm(p){
  p.querySelectorAll(".alarm-key").forEach(function(b){
    b.addEventListener("click",function(e){
      e.preventDefault();
      var d=this.dataset.digit, ci=p.querySelector(".alarm-code-hidden");
      if(!ci)return;
      if(d==="clear")ci.value="";
      else if(d==="backspace")ci.value=ci.value.slice(0,-1);
      else ci.value=(ci.value||"")+d;
      var dis=p.querySelector(".alarm-code-display");
      if(dis){dis.textContent="\u2022".repeat(ci.value.length)||"";dis.style.visibility=ci.value.length?"visible":"hidden";}
      _resetTimer(p);
    });
  });
  var fi=p.querySelector(".alarm-code-input-field");
  if(fi){
    fi.addEventListener("input",function(){
      var ci=p.querySelector(".alarm-code-hidden");
      if(ci)ci.value=fi.value;
      var dis=p.querySelector(".alarm-code-display");
      if(dis){dis.textContent="\u2022".repeat(fi.value.length)||"";dis.style.visibility=fi.value.length?"visible":"hidden";}
      _resetTimer(p);
    });
  }
  _resetTimer(p);
}
function _resetTimer(p){
  if(p._alarmT)clearTimeout(p._alarmT);
  p._alarmT=setTimeout(function(){
    var ci=p.querySelector(".alarm-code-hidden"),fi=p.querySelector(".alarm-code-input-field"),di=p.querySelector(".alarm-code-display");
    if(ci)ci.value="";
    if(fi)fi.value="";
    if(di){di.textContent="";di.style.visibility="hidden";}
  },120000);
}
document.addEventListener("DOMContentLoaded",function(){
  document.querySelectorAll("form.alarm-panel").forEach(_initAlarm);
});
document.addEventListener("htmx:afterSwap",function(e){
  var el=e.target.closest?e.target.closest("form.alarm-panel"):null;
  if(el)_initAlarm(el);
});
})();
</script>