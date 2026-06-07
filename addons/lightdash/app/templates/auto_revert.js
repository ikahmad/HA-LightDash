<script>
var _arTimer=null;
var _rvUrl=$first_view_url;
function resetAr(){if(_arTimer)clearTimeout(_arTimer);_arTimer=setTimeout(function(){window.location.href=_rvUrl},$ar_secs)}
document.addEventListener("touchstart",resetAr,true);
document.addEventListener("click",resetAr,true);
document.addEventListener("scroll",resetAr,true);
document.addEventListener("DOMContentLoaded",resetAr);
</script>
