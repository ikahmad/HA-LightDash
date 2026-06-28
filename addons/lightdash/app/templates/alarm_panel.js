<script>
(function(){
var MAX_CODE=8;
function _dots(panel,n){
  var d=panel.querySelector(".alarm-code-dots");
  if(!d)return;
  var h="";
  for(var k=0;k<MAX_CODE;k++)h+='<span class="alarm-code-dot'+(k<n?" filled":"")+'"></span>';
  d.innerHTML=h;
}
function _initAlarm(p){
  p.querySelectorAll(".alarm-key").forEach(function(b){
    b.addEventListener("click",function(e){
      e.preventDefault();
      var ci=p.querySelector(".alarm-code-hidden");
      if(!ci)return;
      var d=this.dataset.digit;
      if(d==="clear")ci.value="";
      else if(d==="backspace")ci.value=ci.value.slice(0,-1);
      else if(ci.value.length<MAX_CODE)ci.value+=d;
      _dots(p,ci.value.length);
      _resetTimer(p);
    });
  });
  var fi=p.querySelector(".alarm-code-input-field");
  if(fi){
    fi.addEventListener("input",function(){
      var ci=p.querySelector(".alarm-code-hidden");
      if(ci)ci.value=fi.value;
      _dots(p,fi.value.length);
      _resetTimer(p);
    });
  }
  _dots(p,0);
  _resetTimer(p);
}
function _resetTimer(p){
  if(p._alarmT)clearTimeout(p._alarmT);
  p._alarmT=setTimeout(function(){
    var ci=p.querySelector(".alarm-code-hidden"),fi=p.querySelector(".alarm-code-input-field");
    if(ci)ci.value="";
    if(fi)fi.value="";
    _dots(p,0);
  },120000);
}
document.addEventListener("DOMContentLoaded",function(){
  document.querySelectorAll("form.alarm-panel").forEach(_initAlarm);
});
document.addEventListener("htmx:afterSwap",function(e){
  var el=e.target.closest?e.target.closest("form.alarm-panel"):null;
  if(el)_initAlarm(el);
  else document.querySelectorAll("form.alarm-panel").forEach(_initAlarm);
});
})();
</script>
