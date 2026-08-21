(function(){const s=document.getElementById("reactie-form");if(!s)return;const o=s.dataset.email||"",i=document.getElementById("reactie-soort"),t=document.getElementById("reactie-status"),r=s.querySelectorAll(".reactie-set");function a(){const e=i.value;r.forEach(function(t){const n=t.dataset.soort===e;t.hidden=!n,t.querySelectorAll("input, textarea, select").forEach(function(e){e.disabled=!n})})}function e(e){const t=document.getElementById(e);return t&&!t.disabled?t.value.trim():""}function n(n,s){if(e(n))return!0;t&&(t.hidden=!1,t.textContent="Vul «"+s+"» in.");const o=document.getElementById(n);return o&&o.focus(),!1}function c(){const s=i.value;if(s==="vraag")return n("reactie-bericht","Uw vraag of opmerking")?{subject:"[vraag] kalender",body:"Waarover: "+e("reactie-over")+`

`+e("reactie-bericht")}:null;if(s==="correctie"){if(!n("reactie-waar","Waar"))return null;if(!n("reactie-wat","Wat klopt niet"))return null;let t="Waar: "+e("reactie-waar")+`

`+e("reactie-wat");const s=e("reactie-bron-correctie");return s&&(t+=`

Bron: `+s),{subject:"[correctie] "+e("reactie-waar"),body:t}}if(s==="anders")return n("reactie-anders","Uw bericht")?{subject:"[anders] kalender",body:e("reactie-anders")}:null;if(!n("reactie-naam","Naam"))return null;if(!n("reactie-waarom","Waarom hoort deze heilige in de kalender?"))return null;let t="Naam: "+e("reactie-naam")+`
`;const o=e("reactie-feestdag");o&&(t+="Feestdag: "+o+`
`),t+=`
`+e("reactie-waarom");const a=e("reactie-bronnen");return a&&(t+=`

Bronnen: `+a),{subject:"[heilige] "+e("reactie-naam"),body:t}}i.addEventListener("change",a),a(),s.addEventListener("submit",function(e){if(e.preventDefault(),t&&(t.hidden=!0,t.textContent=""),!o)return;const n=c();if(!n)return;const s="mailto:"+o+"?subject="+encodeURIComponent(n.subject)+"&body="+encodeURIComponent(n.body);window.location.href=s,t&&(t.hidden=!1,t.textContent="Als er geen e-mailprogramma opent, stuur het bericht zelf naar "+o+".")})})()