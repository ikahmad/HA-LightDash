// ### Set individual font sizes
let icey_textFit_timeout = null;
function icey_textFit() {
	clearTimeout(icey_textFit_timeout);
	icey_textFit_timeout = setTimeout(function () {
		document.querySelectorAll(".icey_text_fit").forEach(el => {
			el.style.display = "inline-block";
			el.style.whiteSpace = "nowrap";
			if (el.innerText.length === 0) return;

			const parentWidth = el.parentElement.offsetWidth;
			let fontSize = parentWidth;
			let fitPct = parseInt(el.getAttribute("data-fit-pct")) || 0;

			el.style.fontSize = fontSize + "px";

			for (let iter = 0; iter < 10; iter++) {
				const cw = el.offsetWidth;
				if (cw <= 0) break;
				if (cw <= parentWidth) break;
				fontSize = fontSize / (cw / parentWidth);
				el.style.fontSize = fontSize + "px";
			}

			if (fitPct > 0 && fitPct !== 100) {
				fontSize = fontSize * fitPct / 100;
				el.style.fontSize = fontSize + "px";
			}
		});
	}, 10);
}

// ### Clock updates
function uclk(){var n=new Date();document.querySelectorAll(".clock-digital").forEach(function(e){var o={hour:"2-digit",minute:"2-digit",timeZone:e.getAttribute("data-tz")||"Europe/London",hour12:e.getAttribute("data-fmt")!=="24"};if(e.getAttribute("data-sec"))o.second="2-digit";e.textContent=(new Intl.DateTimeFormat("en-GB",o)).format(n)});document.querySelectorAll(".clock-date").forEach(function(e){var df=e.getAttribute("data-dfmt")||"default";if(df==="iso")e.textContent=n.toISOString().split("T")[0];else if(df==="locale")e.textContent=n.toLocaleDateString();else e.textContent=n.toDateString()});if(typeof icey_textFit==="function")icey_textFit()}
setInterval(uclk,30000);
document.addEventListener("DOMContentLoaded",uclk);
document.addEventListener("htmx:afterSwap",uclk);