if (!restoreNavigation()) {
    activatePanel("dashboard");
}

if (window.AnimationsEngine) {
    window.animationsEngine = new AnimationsEngine();
    window.animationsEngine.init();
}
