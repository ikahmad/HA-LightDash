// ### Necessary element styling 
document.querySelectorAll(".icey_text_fit").forEach(el => {
	el.style.display = "inline-block";
	el.style.whiteSpace = "nowrap";
});

// ### Set individual font sizes
let icey_textFit_timeout = null;
function icey_textFit() {
	clearTimeout(icey_textFit_timeout);
	icey_textFit_timeout = setTimeout(function () {
		document.querySelectorAll(".icey_text_fit").forEach(el => {
			if (el.innerText.length === 0) return;

			const parentWidth = el.parentElement.offsetWidth;
			let fontSize = parentWidth;
			el.style.fontSize = fontSize + "px";
			el.style.setProperty("--font_size", fontSize);

			for (let iter = 0; iter < 10; iter++) {
				const cw = el.offsetWidth;
				if (cw <= 0) break;
				if (cw <= parentWidth) break;
				fontSize = fontSize / (cw / parentWidth);
				el.style.fontSize = fontSize + "px";
				el.style.setProperty("--font_size", fontSize);
			}
		});
	}, 10);
}