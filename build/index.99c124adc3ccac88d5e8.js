(()=>{function e(e,n){var r;if("undefined"==typeof Symbol||null==e[Symbol.iterator]){if(Array.isArray(e)||(r=function(e,n){if(e){if("string"==typeof e)return t(e,n);var r=Object.prototype.toString.call(e).slice(8,-1);return"Object"===r&&e.constructor&&(r=e.constructor.name),"Map"===r||"Set"===r?Array.from(e):"Arguments"===r||/^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(r)?t(e,n):void 0}}(e))||n&&e&&"number"==typeof e.length){r&&(e=r);var o=0,i=function(){};return{s:i,n:function(){return o>=e.length?{done:!0}:{done:!1,value:e[o++]}},e:function(e){throw e},f:i}}throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method.")}var a,c=!0,l=!1;return{s:function(){r=e[Symbol.iterator]()},n:function(){var e=r.next();return c=e.done,e},e:function(e){l=!0,a=e},f:function(){try{c||null==r.return||r.return()}finally{if(l)throw a}}}}function t(e,t){(null==t||t>e.length)&&(t=e.length);for(var n=0,r=new Array(t);n<t;n++)r[n]=e[n];return r}var n=JSON.parse(document.getElementById("root-dir").textContent),r=document.getElementById("clearSelections"),o=document.getElementById("compare"),i=document.getElementsByName("checkbox"),a=window.sessionStorage.getItem("checked")||"[]",c=JSON.parse(a),l=!1;function d(){l&&2!==c.length&&(l=!1,function(){var t,n=e(i);try{for(n.s();!(t=n.n()).done;)t.value.disabled=!1}catch(e){n.e(e)}finally{n.f()}}()),l||2!==c.length||(l=!0,function(){l=!0;var t,n=e(i);try{for(n.s();!(t=n.n()).done;){var r=t.value;r.disabled=!0,r.checked&&(r.disabled=!1)}}catch(e){n.e(e)}finally{n.f()}}())}function s(){2!==c.length?(o.href="",o.classList.add("disabled")):(o.href=window.location.protocol+"//"+window.location.host+"/"+n+"compare/"+c[0]+"/"+c[1],o.classList.remove("disabled")),r.disabled=0===c.length}s(),function(){var t,n=e(i);try{for(n.s();!(t=n.n()).done;){var r=t.value;-1!==c.indexOf(r.getAttribute("algorithm"))&&(r.checked=!0),r.onclick=function(){var e=this.getAttribute("algorithm");c.includes(e)?(c=c.filter((function(t){return t!==e})),window.sessionStorage.setItem("checked",JSON.stringify(c))):c.length<2&&(c.push(e),window.sessionStorage.setItem("checked",JSON.stringify(c))),s(),d()}}}catch(e){n.e(e)}finally{n.f()}}(),d(),r.onclick=function(){window.sessionStorage.removeItem("checked"),window.location.reload()}})();