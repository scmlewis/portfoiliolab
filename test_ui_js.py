"""Unit tests for JavaScript functions: dark mode, scroll reveal, magnetic buttons, tabs, tooltips."""
import re
import os
import pytest


JS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'app.js')


@pytest.fixture
def js_content():
    with open(JS_PATH, 'r', encoding='utf-8') as f:
        return f.read()


# ============================================================================
# SCROLL REVEAL
# ============================================================================

class TestScrollRevealJS:
    def test_initScrollReveal_function_exists(self, js_content):
        assert 'function initScrollReveal()' in js_content

    def test_uses_intersection_observer(self, js_content):
        assert 'IntersectionObserver' in js_content

    def test_queries_reveal_elements(self, js_content):
        assert ".reveal" in js_content

    def test_adds_revealed_class(self, js_content):
        assert "'revealed'" in js_content

    def test_unobserves_after_reveal(self, js_content):
        assert 'unobserve' in js_content

    def test_has_threshold(self, js_content):
        assert 'threshold' in js_content

    def test_has_root_margin(self, js_content):
        assert 'rootMargin' in js_content

    def test_called_on_dom_ready(self, js_content):
        assert 'initScrollReveal' in js_content


# ============================================================================
# DARK MODE
# ============================================================================

class TestDarkModeJS:
    def test_toggleDarkMode_function(self, js_content):
        assert 'function toggleDarkMode()' in js_content or 'function initDarkMode()' in js_content

    def test_uses_localStorage(self, js_content):
        assert 'localStorage' in js_content

    def test_toggles_dark_class(self, js_content):
        assert "'dark'" in js_content

    def test_checks_system_preference(self, js_content):
        assert 'prefers-color-scheme' in js_content

    def test_updates_sun_icon(self, js_content):
        assert 'icon-sun' in js_content

    def test_updates_moon_icon(self, js_content):
        assert 'icon-moon' in js_content

    def test_keyboard_shortcut_ctrl_d(self, js_content):
        assert "ctrl && e.key === 'd'" in js_content

    def test_mobile_toggle_support(self, js_content):
        assert 'darkModeToggleMobile' in js_content


# ============================================================================
# MAGNETIC BUTTONS
# ============================================================================

class TestMagneticButtonsJS:
    def test_transform_manipulation(self, js_content):
        assert 'transform' in js_content

    def test_mouseenter_handler(self, js_content):
        assert 'mouseenter' in js_content

    def test_mousemove_handler(self, js_content):
        assert 'mousemove' in js_content

    def test_mouseleave_handler(self, js_content):
        assert 'mouseleave' in js_content

    def test_getBoundingClientRect(self, js_content):
        assert 'getBoundingClientRect' in js_content

    def test_resets_transform_on_leave(self, js_content):
        assert "translate(0, 0)" in js_content or "translate(0,0)" in js_content


# ============================================================================
# TABS
# ============================================================================

class TestTabsJS:
    def test_setupTabs_function(self, js_content):
        assert 'function setupTabs()' in js_content

    def test_switchTab_function(self, js_content):
        assert 'function switchTab(' in js_content

    def test_queries_tab_elements(self, js_content):
        assert '".tab"' in js_content or "'.tab'" in js_content

    def test_queries_tab_panel_elements(self, js_content):
        assert '".tab-panel"' in js_content or "'.tab-panel'" in js_content

    def test_toggles_active_class(self, js_content):
        assert "'active'" in js_content

    def test_hides_inactive_panels(self, js_content):
        assert "'hidden'" in js_content


# ============================================================================
# TOOLTIPS
# ============================================================================

class TestTooltipsJS:
    def test_setupTooltips_function(self, js_content):
        assert 'function setupTooltips()' in js_content

    def test_showTooltip_function(self, js_content):
        assert 'function showTooltip(' in js_content

    def test_hideTooltip_function(self, js_content):
        assert 'function hideTooltip()' in js_content

    def test_tooltip_definitions(self, js_content):
        assert 'TOOLTIP_DEFS' in js_content
        assert 'totalReturn' in js_content
        assert 'sharpeRatio' in js_content

    def test_touch_detection(self, js_content):
        assert 'pointer: coarse' in js_content

    def test_tooltip_trigger_class(self, js_content):
        assert 'tooltip-trigger' in js_content

    def test_creates_tooltip_element(self, js_content):
        assert "tooltip__title" in js_content
        assert "tooltip__desc" in js_content


# ============================================================================
# ADVANCED TOGGLE
# ============================================================================

class TestAdvancedToggleJS:
    def test_setupAdvancedToggle_function(self, js_content):
        assert 'function setupAdvancedToggle()' in js_content

    def test_queries_advanced_section(self, js_content):
        assert 'advancedSection' in js_content

    def test_queries_advanced_toggle(self, js_content):
        assert 'advancedToggle' in js_content

    def test_toggles_collapsed_class(self, js_content):
        assert "'section--collapsed'" in js_content

    def test_toggles_expanded_class(self, js_content):
        assert "'section--expanded'" in js_content


# ============================================================================
# KEYBOARD SHORTCUTS
# ============================================================================

class TestKeyboardShortcuts:
    def test_handleKeyboard_function(self, js_content):
        assert 'function handleKeyboard(' in js_content

    def test_escape_key(self, js_content):
        assert "'Escape'" in js_content

    def test_ctrl_enter_backtest(self, js_content):
        assert "'Enter'" in js_content

    def test_ctrl_d_dark_mode(self, js_content):
        assert "'d'" in js_content

    def test_question_mark_help(self, js_content):
        assert "'?'" in js_content


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

class TestUtilities:
    def test_debounce_function(self, js_content):
        assert 'function debounce(' in js_content

    def test_abort_previous(self, js_content):
        assert 'function abortPrevious()' in js_content

    def test_fmt_function(self, js_content):
        assert 'function fmt(' in js_content

    def test_setBtnLoading_function(self, js_content):
        assert 'function setBtnLoading(' in js_content


# ============================================================================
# ONBOARDING
# ============================================================================

class TestOnboardingJS:
    def test_setupOnboarding_function(self, js_content):
        assert 'function setupOnboarding()' in js_content

    def test_onboarding_steps(self, js_content):
        assert 'ONBOARDING_STEPS' in js_content

    def test_onboarding_close(self, js_content):
        assert 'function onboardingClose()' in js_content

    def test_saves_to_localStorage(self, js_content):
        assert 'portfoliolab_onboarded' in js_content


# ============================================================================
# MOBILE FAB
# ============================================================================

class TestMobileFAB:
    def test_setupMobileFab_function(self, js_content):
        assert 'function setupMobileFab()' in js_content

    def test_cleanupMobileFab_function(self, js_content):
        assert 'function cleanupMobileFab()' in js_content

    def test_fab_intersection_observer(self, js_content):
        assert 'fabIntersectionObserver' in js_content


# ============================================================================
# INITIALIZATION
# ============================================================================

class TestInitialization:
    def test_init_function(self, js_content):
        assert 'function init()' in js_content

    def test_dom_ready_listener(self, js_content):
        assert "addEventListener('DOMContentLoaded'" in js_content

    def test_calls_setupEventListeners(self, js_content):
        assert 'setupEventListeners' in js_content

    def test_calls_setupTabs(self, js_content):
        assert 'setupTabs' in js_content

    def test_calls_setupTooltips(self, js_content):
        assert 'setupTooltips' in js_content

    def test_calls_setupAdvancedToggle(self, js_content):
        assert 'setupAdvancedToggle' in js_content

    def test_calls_setupMobileFab(self, js_content):
        assert 'setupMobileFab' in js_content

    def test_calls_setupOnboarding(self, js_content):
        assert 'setupOnboarding' in js_content


# ============================================================================
# BANNED PATTERNS IN JS
# ============================================================================

class TestBannedPatternsJS:
    def test_no_banned_material_icons(self, js_content):
        assert 'material-symbols' not in js_content.lower()

    def test_no_roboto(self, js_content):
        assert 'Roboto' not in js_content

    def test_uses_svg_for_icons(self, js_content):
        assert 'createElementNS' in js_content or '<svg' in js_content or 'svg' in js_content.lower()
