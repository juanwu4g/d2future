// d2future homepage — contact form submission + lightweight JP/EN toggle.
// Vanilla JS, no dependencies, no build step.

(function () {
  "use strict";

  // --- Current year in the footer ---------------------------------------
  const yearEl = document.getElementById("year");
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // --- Contact form -> POST /api/contact --------------------------------
  const form = document.getElementById("contact-form");
  const status = document.getElementById("form-status");

  if (form) {
    form.addEventListener("submit", async function (event) {
      event.preventDefault();
      setStatus("", "");

      const payload = {
        name: form.name.value.trim(),
        email: form.email.value.trim(),
        message: form.message.value.trim(),
      };

      const submitBtn = form.querySelector("button[type='submit']");
      submitBtn.disabled = true;

      try {
        const res = await fetch("/api/contact", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });

        if (res.ok) {
          form.reset();
          setStatus(t("status.success"), "success");
        } else if (res.status === 422) {
          setStatus(t("status.invalid"), "error");
        } else {
          setStatus(t("status.error"), "error");
        }
      } catch (err) {
        setStatus(t("status.error"), "error");
      } finally {
        submitBtn.disabled = false;
      }
    });
  }

  function setStatus(message, kind) {
    if (!status) return;
    status.textContent = message;
    status.className = "form-status" + (kind ? " " + kind : "");
  }

  // --- JP/EN toggle ------------------------------------------------------
  // Translations keyed by the data-i18n attribute on each element. English is
  // the source of truth in the HTML; Japanese is applied on toggle.
  const I18N = {
    en: {
      "skip": "Skip to content",
      "nav.about": "About",
      "nav.services": "Services",
      "nav.contact": "Contact",
      "nav.cta": "Let's talk",
      "hero.eyebrow": "Tokyo · Forward-Deployed Engineering",
      "hero.title": "We embed with your team and ship.",
      "hero.lede":
        "d2future is a forward-deployed engineering firm building AI agents, cloud native platforms, and data systems — in production, alongside you.",
      "hero.cta": "Start a conversation",
      "stats.engineers": "Senior engineers",
      "stats.areas": "Focus areas",
      "stats.shipped": "Systems shipped to production",
      "about.title": "About",
      "about.p1":
        "We are a small team of senior engineers based in Tokyo. We work the way the best internal teams do: embedded, accountable, and close to the problem — not handing over slides and walking away.",
      "about.p2":
        "Our focus is narrow on purpose. We take on work in AI agents, cloud native infrastructure, and data engineering, where deep practice beats broad coverage. We ship to production and stay until it runs.",
      "about.p3":
        "Reserved by temperament, direct in our work. We would rather earn trust through systems that hold up than through promises that sound good in a meeting.",
      "facts.company": "Company",
      "facts.founded": "Founded",
      "facts.founded.value": "2021",
      "facts.location": "Location",
      "facts.location.value": "Tokyo, Japan",
      "facts.team": "Team",
      "facts.team.value": "12 engineers",
      "facts.business": "Business",
      "facts.business.value":
        "Forward-deployed engineering for AI agents, cloud native systems, and data platforms",
      "services.title": "Services",
      "services.ai.title": "AI Agent Engineering",
      "services.ai.body":
        "Production agents that do real work — tool use, retrieval, and evaluation built in. We design for reliability, not demos.",
      "services.cloud.title": "Cloud Native",
      "services.cloud.body":
        "Containers, CI/CD, and observability done well. Infrastructure your team can operate, scale, and reason about with confidence.",
      "services.data.title": "Data Engineering",
      "services.data.body":
        "Pipelines and platforms that turn raw data into something teams trust — tested, documented, and ready for analytics and AI.",
      "contact.title": "Contact",
      "contact.intro": "Tell us what you are building. We read every message.",
      "contact.name": "Name",
      "contact.email": "Email",
      "contact.message": "Message",
      "contact.submit": "Send message",
      "footer.location": "Tokyo, Japan",
      "status.success": "Thanks — your message was sent.",
      "status.invalid": "Please check your name, email, and message.",
      "status.error": "Something went wrong. Please try again.",
    },
    ja: {
      "skip": "本文へスキップ",
      "nav.about": "会社概要",
      "nav.services": "サービス",
      "nav.contact": "お問い合わせ",
      "nav.cta": "相談する",
      "hero.eyebrow": "東京・フォワードデプロイド・エンジニアリング",
      "hero.title": "チームに入り込み、形にする。",
      "hero.lede":
        "d2future は、AIエージェント・クラウドネイティブ・データ基盤を、お客様と共に本番環境で構築するフォワードデプロイド・エンジニアリングファームです。",
      "hero.cta": "相談をはじめる",
      "stats.engineers": "シニアエンジニア",
      "stats.areas": "注力領域",
      "stats.shipped": "本番投入したシステム",
      "about.title": "会社概要",
      "about.p1":
        "私たちは東京を拠点とする少数精鋭のシニアエンジニアチームです。資料を渡して終わりではなく、現場に入り込み、責任を持って課題に向き合います。",
      "about.p2":
        "対象領域はあえて絞っています。AIエージェント、クラウドネイティブ基盤、データエンジニアリング。広く浅くより、深い実践を重視します。本番に届け、動くまで伴走します。",
      "about.p3":
        "控えめな気質、実務には率直に。聞こえの良い約束ではなく、確かに動き続けるシステムで信頼を得たいと考えています。",
      "facts.company": "会社名",
      "facts.founded": "設立",
      "facts.founded.value": "2021年",
      "facts.location": "所在地",
      "facts.location.value": "東京都",
      "facts.team": "メンバー",
      "facts.team.value": "エンジニア12名",
      "facts.business": "事業内容",
      "facts.business.value":
        "AIエージェント・クラウドネイティブ・データ基盤のフォワードデプロイド・エンジニアリング",
      "services.title": "サービス",
      "services.ai.title": "AIエージェント開発",
      "services.ai.body":
        "実務をこなす本番向けエージェント。ツール利用・検索・評価を組み込み、デモではなく信頼性を前提に設計します。",
      "services.cloud.title": "クラウドネイティブ",
      "services.cloud.body":
        "コンテナ、CI/CD、オブザーバビリティを丁寧に。チームが運用・拡張・把握できる基盤を構築します。",
      "services.data.title": "データエンジニアリング",
      "services.data.body":
        "生のデータを信頼できる資産へ。テストされ、文書化され、分析とAIに使えるパイプラインと基盤を構築します。",
      "contact.title": "お問い合わせ",
      "contact.intro": "構想をお聞かせください。すべてのメッセージに目を通します。",
      "contact.name": "お名前",
      "contact.email": "メールアドレス",
      "contact.message": "メッセージ",
      "contact.submit": "送信する",
      "footer.location": "東京, 日本",
      "status.success": "ありがとうございます。メッセージを送信しました。",
      "status.invalid": "お名前・メール・メッセージをご確認ください。",
      "status.error": "エラーが発生しました。もう一度お試しください。",
    },
  };

  let lang = "en";

  function t(key) {
    return (I18N[lang] && I18N[lang][key]) || I18N.en[key] || "";
  }

  function applyLanguage(next) {
    lang = next;
    document.documentElement.lang = next;
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      const key = el.getAttribute("data-i18n");
      const value = t(key);
      if (value) el.textContent = value;
    });
    const toggle = document.getElementById("lang-toggle");
    if (toggle) {
      // Show the language you can switch TO.
      toggle.textContent = next === "en" ? "日本語" : "English";
    }
  }

  const toggle = document.getElementById("lang-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      applyLanguage(lang === "en" ? "ja" : "en");
    });
  }
})();
