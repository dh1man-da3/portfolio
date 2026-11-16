// Original interactive behavior, adapted for a static multi-page site.

// In-page links are smooth-scrolled without interfering with navigation.
document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach((link) => {
    link.addEventListener("click", (event) => {
        const target = document.getElementById(link.getAttribute("href").slice(1));
        if (!target) return;
        event.preventDefault();
        target.scrollIntoView({
            behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
        });
    });
});

// Original skill-bar animation (not run for visitors requesting reduced motion).
window.addEventListener("load", () => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    document.querySelectorAll(".skill-progress").forEach((bar) => {
        const finalWidth = bar.style.width;
        bar.style.width = "0";
        setTimeout(() => {
            bar.style.transition = "width 1.2s ease";
            bar.style.width = finalWidth;
        }, 200);
    });
});

// Original button hover effect.
document.querySelectorAll(".btn-primary, .contact-button").forEach((button) => {
    button.addEventListener("mouseenter", () => {
        if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
        button.style.transform = "scale(1.03)";
        button.style.transition = "0.15s";
    });
    button.addEventListener("mouseleave", () => {
        button.style.transform = "scale(1)";
    });
});

// GitHub Pages cannot process a server-side contact form. Instead, prepare an
// email in the visitor's email application; the visitor must click Send there.
const contactForm = document.querySelector("[data-contact-form]");
if (contactForm) {
    contactForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const feedback = contactForm.querySelector(".form-feedback");
        const recipient = contactForm.dataset.recipient?.trim() ?? "";
        feedback.hidden = false;

        if (!recipient || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(recipient)) {
            feedback.textContent = "Contact email is not configured. Please use an available social link instead.";
            return;
        }

        const formData = new FormData(contactForm);
        const name = String(formData.get("name") ?? "").trim();
        const email = String(formData.get("email") ?? "").trim();
        const subject = String(formData.get("subject") ?? "").trim();
        const message = String(formData.get("message") ?? "").trim();
        const body = `From: ${name}\nReply-to: ${email}\n\n${message}`;
        const mailtoUrl = `mailto:${recipient}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

        feedback.textContent = "Your email application should open with a draft. Review the message and click Send in your email application to actually send it.";
        window.location.href = mailtoUrl;
    });
}
