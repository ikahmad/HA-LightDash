<script>
function ss(e){
var s=e.target;
if(!s||!s.classList.contains("entity-state"))return;
var c=s.closest(".tile-card");
if(!c)return;
var r=c.querySelector(".feature-slider");
if(!r)return;
var eid=s.getAttribute("data-entity");
if(!eid)return;
fetch('$state_api_url'+eid).then(function(resp){return resp.json()}).then(function(d){
if(d&&d.attributes&&d.attributes.brightness){r.value=Math.round(d.attributes.brightness/255*100);}
});
}
document.addEventListener("htmx:sseMessage",ss);
</script>
