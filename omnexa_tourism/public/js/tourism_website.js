/* global frappe */
(function () {
	const STORAGE_LANG = "tourism_site_lang";

	const DEFAULT_CATALOG = {
		destinations: [
			{ key: "hotels", name_ar: "فنادق", name_en: "Hotels", icon: "🏨", desc: "Luxury stays" },
			{ key: "flights", name_ar: "رحلات جوية", name_en: "Flights", icon: "✈️", desc: "Global destinations" },
			{ key: "beaches", name_ar: "شواطئ", name_en: "Beaches", icon: "🏖️", desc: "Coastal paradise" },
			{ key: "activities", name_ar: "أنشطة", name_en: "Activities", icon: "🎯", desc: "Adventures" },
		],
		services: [
			{ icon: "🏨", ar: "حجز فنادق", en: "Hotel Booking" },
			{ icon: "✈️", ar: "تذاكر طيران", en: "Flight Tickets" },
			{ icon: "🚗", ar: "تأجير سيارات", en: "Car Rental" },
			{ icon: "🎫", ar: "أنشطة ترفيهية", en: "Entertainment" },
			{ icon: "🍽️", ar: "حجوزات مطاعم", en: "Restaurant Reservations" },
			{ icon: "📱", ar: "تطبيق المسافر", en: "Traveler App" },
		],
	};

	window.TourismSite = {
		config: null,
		lang: localStorage.getItem(STORAGE_LANG) || "ar",
		page: "home",

		init(page) {
			this.page = page || "home";
			this.config = this.defaultConfig();
			this.applyTheme();
			this.renderChrome();
			this.loadConfig()
				.then(() => {
					this.applyTheme();
					this.renderChrome();
					const fn = this[`init_${this.page}`];
					if (typeof fn === "function") fn.call(this);
					this.setupReveal();
				})
				.catch(() => {
					this.config = this.config || this.defaultConfig();
					this.renderChrome();
					const fn = this[`init_${this.page}`];
					if (typeof fn === "function") fn.call(this);
					this.setupReveal();
				});
		},

		defaultConfig() {
			return {
				brand_name_ar: "Omnexa Tourism",
				brand_name_en: "Omnexa Tourism",
				tagline_ar: "اكتشف العالم معنا",
				tagline_en: "Discover the world with us",
				hero_text_ar: "من الفنادق الفاخرة إلى الرحلات الجوية — كل ما تحتاجه لرحلة لا تُنسى",
				hero_text_en: "From luxury hotels to flights — everything you need for an unforgettable journey",
				hero_image: "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=1920&q=85",
				logo: "/assets/omnexa_tourism/logo.png",
				primary_color: "#00bcd4",
				secondary_color: "#0097a7",
				accent_color: "#00bcd4",
				gold_color: "#ffc107",
				destinations: DEFAULT_CATALOG.destinations,
				services: DEFAULT_CATALOG.services,
				stats: { destinations: 100, travelers: 50000, partners: 200, years: 12 },
			};
		},

		t(key) {
			const map = {
				home: { ar: "الرئيسية", en: "Home" },
				destinations: { ar: "الوجهات", en: "Destinations" },
				services: { ar: "الخدمات", en: "Services" },
				contact: { ar: "تواصل", en: "Contact" },
				login: { ar: "دخول", en: "Login" },
				book: { ar: "احجز الآن", en: "Book Now" },
				learn_more: { ar: "اعرف المزيد", en: "Learn More" },
				destinations: { ar: "وجهة", en: "Destinations" },
				travelers: { ar: "مسافر", en: "Travelers" },
				partners: { ar: "شريك", en: "Partners" },
				years: { ar: "سنة", en: "Years" },
				loading: { ar: "جاري التحميل...", en: "Loading..." },
			};
			return (map[key] && map[key][this.lang]) || key;
		},

		esc(v) {
			if (typeof frappe !== "undefined" && frappe.utils && frappe.utils.escape_html) {
				return frappe.utils.escape_html(v == null ? "" : String(v));
			}
			const d = document.createElement("div");
			d.textContent = v == null ? "" : String(v);
			return d.innerHTML;
		},

		nameField() {
			return this.lang === "ar" ? "brand_name_ar" : "brand_name_en";
		},

		textField(base) {
			return this.lang === "ar" ? `${base}_ar` : `${base}_en`;
		},

		async loadConfig() {
			try {
				if (typeof frappe !== "undefined" && frappe.call) {
					const r = await frappe.call({
						method: "omnexa_tourism.api.public_tourism_site.get_site_config",
					});
					this.config = Object.assign(this.defaultConfig(), r.message || {});
				} else {
					const res = await fetch("/api/method/omnexa_tourism.api.public_tourism_site.get_site_config");
					const data = await res.json();
					this.config = Object.assign(this.defaultConfig(), data.message || {});
				}
			} catch (e) {
				this.config = this.config || this.defaultConfig();
			}
			if (this.config.primary_color) {
				document.documentElement.style.setProperty("--tourism-primary", this.config.primary_color);
			}
			if (this.config.secondary_color) {
				document.documentElement.style.setProperty("--tourism-secondary", this.config.secondary_color);
			}
			if (this.config.accent_color) {
				document.documentElement.style.setProperty("--tourism-teal", this.config.accent_color);
			}
			if (this.config.gold_color) {
				document.documentElement.style.setProperty("--tourism-gold", this.config.gold_color);
			}
		},

		applyTheme() {
			const root = document.querySelector(".tourism-site");
			if (!root) return;
			root.dir = this.lang === "ar" ? "rtl" : "ltr";
			root.lang = this.lang;
		},

		toggleLang() {
			this.lang = this.lang === "ar" ? "en" : "ar";
			localStorage.setItem(STORAGE_LANG, this.lang);
			this.applyTheme();
			this.renderChrome();
			const fn = this[`init_${this.page}`];
			if (typeof fn === "function") fn.call(this);
		},

		setupReveal() {
			const els = document.querySelectorAll(".tourism-reveal");
			if (!els.length || !("IntersectionObserver" in window)) {
				els.forEach((el) => el.classList.add("tourism-visible"));
				return;
			}
			const obs = new IntersectionObserver(
				(entries) => {
					entries.forEach((e) => {
						if (e.isIntersecting) {
							e.target.classList.add("tourism-visible");
							obs.unobserve(e.target);
						}
					});
				},
				{ threshold: 0.12 }
			);
			els.forEach((el) => obs.observe(el));
		},

		renderChrome() {
			const cfg = this.config || this.defaultConfig();
			const name = cfg[this.nameField()] || "Tourism";
			const logo = cfg.logo
				? `<img src="${this.esc(cfg.logo)}" alt="" onerror="this.style.display='none'">`
				: "✈️";
			const nav = [
				{ href: "/tourism", key: "home", page: "home" },
				{ href: "/tourism#tourism-destinations-section", key: "destinations", page: "home" },
				{ href: "/tourism#tourism-services-section", key: "services", page: "home" },
				{ href: "/tourism#tourism-stats", key: "stats", page: "home" },
			];

			const header = document.getElementById("tourism-header");
			if (header) {
				header.innerHTML = `
					<div class="tourism-topbar"><div class="tourism-wrap tourism-topbar-inner">
						<span>📞 +966 11 000 0000</span>
						<span>✉ bookings@omnexa.tourism</span>
						<span class="tourism-topbar-links">
							<a href="/app/tourism-workcenter">${this.lang === "ar" ? "مركز العمل" : "Workcenter"}</a>
							<a href="/app/tourism-traveler-portal">${this.lang === "ar" ? "بوابة المسافرين" : "Traveler Portal"}</a>
						</span>
					</div></div>
					<div class="tourism-wrap tourism-header-inner">
						<a class="tourism-brand tourism-brand-stack" href="/tourism">
							<span class="tourism-brand-logo">${logo}</span>
							<span class="tourism-brand-name">${this.esc(name)}</span>
						</a>
						<button type="button" class="tourism-mobile-toggle" id="tourism-menu-toggle" aria-label="Menu">☰</button>
						<nav class="tourism-nav tourism-nav-single" id="tourism-nav">
							<div class="tourism-nav-links">
							${nav
								.map((n) => {
									const label = this.t(n.key);
									const active = n.page && this.page === n.page ? "active" : "";
									return `<a href="${n.href}" class="${active}">${label}</a>`;
								})
								.join("")}
							</div>
						</nav>
						<div class="tourism-actions">
							<button type="button" class="tourism-lang" id="tourism-lang-toggle">${this.lang === "ar" ? "EN" : "AR"}</button>
							<a class="tourism-btn tourism-btn-outline" href="/login">${this.t("login")}</a>
							<a class="tourism-btn tourism-btn-primary" href="/app/tourism-workcenter">${this.t("book")}</a>
						</div>
					</div>`;
				document.getElementById("tourism-lang-toggle")?.addEventListener("click", () => this.toggleLang());
				document.getElementById("tourism-menu-toggle")?.addEventListener("click", () => {
					document.getElementById("tourism-nav")?.classList.toggle("open");
				});
			}

			const footer = document.getElementById("tourism-footer");
			if (footer) {
				footer.innerHTML = `
					<div class="tourism-wrap tourism-footer-grid">
						<div>
							<h3>${this.esc(name)}</h3>
							<p>${this.esc(cfg[this.textField("hero_text")] || "")}</p>
							<p class="tourism-footer-contact">📞 +966 11 000 0000 · ✉ bookings@omnexa.tourism</p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "الوجهات" : "Destinations"}</h4>
							<p><a href="/tourism#tourism-destinations-section">${this.lang === "ar" ? "فنادق" : "Hotels"}</a></p>
							<p><a href="/tourism#tourism-destinations-section">${this.lang === "ar" ? "رحلات جوية" : "Flights"}</a></p>
							<p><a href="/tourism#tourism-destinations-section">${this.lang === "ar" ? "شواطئ" : "Beaches"}</a></p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "الخدمات" : "Services"}</h4>
							<p><a href="/tourism#tourism-services-section">${this.lang === "ar" ? "حجز فنادق" : "Hotel Booking"}</a></p>
							<p><a href="/tourism#tourism-services-section">${this.lang === "ar" ? "تذاكر طيران" : "Flight Tickets"}</a></p>
							<p><a href="/tourism#tourism-services-section">${this.lang === "ar" ? "تأجير سيارات" : "Car Rental"}</a></p>
						</div>
						<div>
							<h4>${this.lang === "ar" ? "البوابات" : "Portals"}</h4>
							<p><a href="/app/tourism-workcenter">${this.lang === "ar" ? "مركز العمل" : "Workcenter"}</a></p>
							<p><a href="/app/tourism-traveler-portal">${this.lang === "ar" ? "بوابة المسافرين" : "Traveler Portal"}</a></p>
						</div>
					</div>
					<div class="tourism-wrap tourism-footer-bottom">© ${new Date().getFullYear()} ${this.esc(name)} · Omnexa · ErpGenEx</div>`;
			}
		},

		init_home() {
			const cfg = this.config || {};
			const heroImg = cfg.hero_image || "";
			const hero = document.getElementById("tourism-hero");
			if (hero) {
				hero.innerHTML = `
					<div class="tourism-hero-bg" style="background-image:url('${this.esc(heroImg)}')"></div>
					<div class="tourism-hero-overlay"></div>
					<div class="tourism-wrap tourism-hero-premium-inner">
						<span class="tourism-eyebrow tourism-eyebrow-light">Omnexa Tourism · Premium Travel</span>
						<h1>${this.esc(cfg[this.textField("tagline")] || "")}</h1>
						<p class="tourism-hero-lead">${this.esc(cfg[this.textField("hero_text")] || "")}</p>
						<div class="tourism-hero-cta">
							<a class="tourism-btn tourism-btn-accent" href="/app/tourism-workcenter">${this.lang === "ar" ? "احجز الآن" : "Book Now"}</a>
							<a class="tourism-btn tourism-btn-ghost-light" href="/tourism#tourism-destinations-section">${this.lang === "ar" ? "استكشف الوجهات" : "Explore Destinations"}</a>
						</div>
					</div>`;
			}

			const trust = document.getElementById("tourism-trust-strip");
			if (trust) {
				const values = (cfg.services || DEFAULT_CATALOG.services).slice(0, 5);
				trust.innerHTML = `<div class="tourism-wrap tourism-value-inner">${values
					.map((v) => `<div class="tourism-value-item"><span>${v.icon}</span><strong>${this.lang === "ar" ? v.ar : v.en}</strong></div>`)
					.join("")}</div>`;
			}

			const destinations = document.getElementById("tourism-destinations-section");
			if (destinations) {
				const dests = cfg.destinations || DEFAULT_CATALOG.destinations;
				destinations.innerHTML = `
					<div class="tourism-wrap">
						<div class="tourism-section-title">
							<span class="tourism-eyebrow">Our Destinations</span>
							<h2>${this.lang === "ar" ? "وجهاتنا السياحية" : "Our Tourist Destinations"}</h2>
							<p>${this.lang === "ar" ? "مجموعة متنوعة من الوجهات السياحية حول العالم" : "A diverse range of tourist destinations around the world"}</p>
						</div>
						<div class="tourism-grid-4">${dests
							.map((d) => `<div class="tourism-card">
								<div style="font-size:48px;margin-bottom:16px;">${d.icon}</div>
								<h3>${this.esc(this.lang === "ar" ? d.name_ar : d.name_en)}</h3>
								<p>${this.esc(d.desc || "")}</p>
							</div>`
							)
							.join("")}</div>
					</div>`;
			}

			const services = document.getElementById("tourism-services-section");
			if (services) {
				const srvs = cfg.services || DEFAULT_CATALOG.services;
				services.innerHTML = `
					<div class="tourism-wrap">
						<div class="tourism-section-title">
							<span class="tourism-eyebrow">Why Choose Us</span>
							<h2>${this.lang === "ar" ? "لماذا تختارنا؟" : "Why Choose Us?"}</h2>
							<p>${this.lang === "ar" ? "نقدم أفضل خدمات السفر مع راحة تامة" : "We provide the best travel services with complete peace of mind"}</p>
						</div>
						<div class="tourism-grid-4">${srvs
							.map((s) => `<div class="tourism-card">
								<div style="font-size:32px;margin-bottom:12px;">${s.icon}</div>
								<h3>${this.esc(this.lang === "ar" ? s.ar : s.en)}</h3>
							</div>`
							)
							.join("")}</div>
					</div>`;
			}

			const stats = document.getElementById("tourism-stats");
			if (stats && cfg.stats) {
				const s = cfg.stats;
				stats.innerHTML = `
					<div class="tourism-wrap tourism-stats-grid">
						<div><div class="tourism-stat-num">${s.destinations || 0}</div><div class="tourism-stat-label">${this.t("destinations")}</div></div>
						<div><div class="tourism-stat-num">${s.travelers || 0}</div><div class="tourism-stat-label">${this.t("travelers")}</div></div>
						<div><div class="tourism-stat-num">${s.partners || 0}</div><div class="tourism-stat-label">${this.t("partners")}</div></div>
						<div><div class="tourism-stat-num">${s.years || 0}</div><div class="tourism-stat-label">${this.t("years")}</div></div>
					</div>`;
			}

			const cta = document.getElementById("tourism-cta-band");
			if (cta) {
				cta.innerHTML = `
					<div class="tourism-wrap">
						<h2>${this.lang === "ar" ? "جاهز لرحلتك القادمة؟" : "Ready for your next journey?"}</h2>
						<p>${this.lang === "ar" ? "انضم إلى آلاف المسافرين الراضين عن خدماتنا" : "Join thousands of satisfied travelers with our services"}</p>
						<div class="tourism-hero-cta">
							<a class="tourism-btn tourism-btn-accent" href="/app/tourism-workcenter">${this.lang === "ar" ? "احجز الآن" : "Book Now"}</a>
							<a class="tourism-btn tourism-btn-ghost-light" href="/tourism#tourism-services-section">${this.t("learn_more")}</a>
						</div>
					</div>`;
			}
		},
	};
})();
