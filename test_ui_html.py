"""Unit tests for Flask app routes, templates, and HTML structure."""
import sys
import os
import re
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


@pytest.fixture
def index_html(client):
    r = client.get('/')
    return r.data.decode('utf-8')


# ============================================================================
# TEMPLATE RENDERING
# ============================================================================

class TestTemplateRendering:
    def test_index_returns_200(self, client):
        r = client.get('/')
        assert r.status_code == 200

    def test_index_is_html(self, client):
        r = client.get('/')
        assert 'text/html' in r.content_type

    def test_index_contains_app_shell(self, index_html):
        assert 'class="app"' in index_html

    def test_index_contains_main(self, index_html):
        assert 'class="main"' in index_html

    def test_index_contains_grid(self, index_html):
        assert 'class="grid"' in index_html


# ============================================================================
# FLOATING GLASS NAV
# ============================================================================

class TestFloatingNav:
    def test_nav_element_exists(self, index_html):
        assert '<nav' in index_html
        assert 'class="nav"' in index_html

    def test_nav_has_id(self, index_html):
        assert 'id="mainNav"' in index_html

    def test_nav_brand_exists(self, index_html):
        assert 'nav__brand' in index_html

    def test_nav_title_text(self, index_html):
        assert 'PortfolioLab' in index_html

    def test_nav_links_exist(self, index_html):
        assert 'nav__links' in index_html

    def test_dark_mode_toggle_exists(self, index_html):
        assert 'id="darkModeToggle"' in index_html

    def test_hamburger_exists(self, index_html):
        assert 'id="navHamburger"' in index_html

    def test_mobile_overlay_exists(self, index_html):
        assert 'id="navOverlay"' in index_html

    def test_mobile_dark_mode_toggle(self, index_html):
        assert 'id="darkModeToggleMobile"' in index_html


# ============================================================================
# DOUBLE-BEZEL CARDS
# ============================================================================

class TestDoubleBezelHTML:
    def test_card_outer_elements(self, index_html):
        assert index_html.count('class="card-outer"') >= 3, "Should have at least 3 card-outer elements"

    def test_card_inner_elements(self, index_html):
        assert index_html.count('class="card-inner"') >= 3, "Should have at least 3 card-inner elements"

    def test_sections_have_eyebrow(self, index_html):
        assert 'eyebrow' in index_html

    def test_section_titles_exist(self, index_html):
        assert 'Portfolio Setup' in index_html
        assert 'Strategy' in index_html
        assert 'Advanced' in index_html


# ============================================================================
# PHOSPHOR SVG ICONS
# ============================================================================

class TestPhosphorIcons:
    def test_no_material_icons_font(self, index_html):
        assert 'Material+Symbols+Rounded' not in index_html
        assert 'material-symbols' not in index_html.lower()

    def test_inline_svgs_present(self, index_html):
        assert '<svg' in index_html

    def test_svg_use_stroke(self, index_html):
        assert 'stroke="currentColor"' in index_html

    def test_svg_viewbox(self, index_html):
        assert 'viewBox="0 0 24 24"' in index_html


# ============================================================================
# BUTTON-IN-BUTTON PATTERN
# ============================================================================

class TestButtonInButton:
    def test_backtest_button_exists(self, index_html):
        assert 'id="backtestBtn"' in index_html

    def test_backtest_button_has_group_class(self, index_html):
        match = re.search(r'id="backtestBtn"[^>]*class="[^"]*group[^"]*"', index_html)
        assert match, "backtestBtn should have 'group' class"

    def test_btn_icon_exists(self, index_html):
        assert 'btn-icon' in index_html

    def test_btn_icon_contains_svg(self, index_html):
        match = re.search(r'class="btn-icon"[^>]*>.*?<svg', index_html, re.DOTALL)
        assert match, "btn-icon should contain an SVG"


# ============================================================================
# SCROLL REVEAL CLASSES
# ============================================================================

class TestScrollRevealHTML:
    def test_sections_have_reveal_class(self, index_html):
        assert 'class="section reveal' in index_html

    def test_reveal_delay_classes(self, index_html):
        assert 'reveal-delay-1' in index_html
        assert 'reveal-delay-2' in index_html


# ============================================================================
# FORM ELEMENTS
# ============================================================================

class TestFormElementsHTML:
    def test_strategy_select_exists(self, index_html):
        assert 'id="strategySelect"' in index_html

    def test_initial_capital_input(self, index_html):
        assert 'id="initialCapital"' in index_html

    def test_date_inputs(self, index_html):
        assert 'id="startDate"' in index_html
        assert 'id="endDate"' in index_html

    def test_symbol_input_exists(self, index_html):
        assert 'id="symbolText"' in index_html

    def test_text_input_classes(self, index_html):
        assert 'text-input' in index_html

    def test_select_input_class(self, index_html):
        assert 'select-input' in index_html


# ============================================================================
# GEIST FONT
# ============================================================================

class TestGeistFont:
    def test_geist_font_link(self, index_html):
        assert 'Geist' in index_html

    def test_no_roboto_font(self, index_html):
        assert 'Roboto' not in index_html


# ============================================================================
# RESULT PANEL STRUCTURE
# ============================================================================

class TestResultPanel:
    def test_result_panel_exists(self, index_html):
        assert 'result-panel' in index_html

    def test_tabs_exist(self, index_html):
        assert 'data-tab="backtest"' in index_html
        assert 'data-tab="optimization"' in index_html

    def test_metric_cards_structure(self, index_html):
        assert 'id="totalReturn"' in index_html
        assert 'id="annualReturn"' in index_html
        assert 'id="maxDD"' in index_html or 'id="maxDrawdown"' in index_html
        assert 'id="sharpeRatio"' in index_html

    def test_chart_canvas_exists(self, index_html):
        assert 'id="equityChart"' in index_html

    def test_empty_state_exists(self, index_html):
        assert 'id="emptyState"' in index_html


# ============================================================================
# ADVANCED SECTION
# ============================================================================

class TestAdvancedSection:
    def test_advanced_toggle_exists(self, index_html):
        assert 'id="advancedToggle"' in index_html

    def test_advanced_body_hidden(self, index_html):
        assert 'id="advancedBody"' in index_html

    def test_compare_button_exists(self, index_html):
        assert 'id="compareSelectedBtn"' in index_html

    def test_optimize_button_exists(self, index_html):
        assert 'id="optimizeBtn"' in index_html

    def test_frontier_button_exists(self, index_html):
        assert 'id="frontierBtn"' in index_html


# ============================================================================
# CSS & JS REFERENCES
# ============================================================================

class TestAssetReferences:
    def test_css_link(self, index_html):
        assert '/static/style.css' in index_html

    def test_chart_js(self, index_html):
        assert 'chart.js' in index_html

    def test_app_js_not_inline(self, index_html):
        assert '<script src="/static/app.js">' in index_html or 'app.js' in index_html

    def test_viewport_meta(self, index_html):
        assert 'viewport' in index_html

    def test_theme_color_meta(self, index_html):
        assert 'theme-color' in index_html


# ============================================================================
# API ROUTES
# ============================================================================

class TestAPIRoutes:
    def test_asset_types_api(self, client):
        r = client.get('/api/asset-types')
        assert r.status_code == 200

    def test_strategies_api(self, client):
        r = client.get('/api/strategies')
        assert r.status_code == 200

    def test_default_symbols_api(self, client):
        r = client.get('/api/default-symbols')
        assert r.status_code == 200

    def test_symbols_autocomplete_api(self, client):
        r = client.get('/api/symbols-autocomplete?q=AAPL')
        assert r.status_code == 200

    def test_popular_symbols_api(self, client):
        r = client.get('/api/popular-symbols')
        assert r.status_code == 200


# ============================================================================
# DARK MODE SUPPORT IN HTML
# ============================================================================

class TestDarkModeHTML:
    def test_dark_mode_toggle_button(self, index_html):
        assert 'darkModeToggle' in index_html

    def test_sun_moon_icons(self, index_html):
        assert 'icon-sun' in index_html
        assert 'icon-moon' in index_html

    def test_meta_theme_color_light(self, index_html):
        assert 'prefers-color-scheme: light' in index_html

    def test_meta_theme_color_dark(self, index_html):
        assert 'prefers-color-scheme: dark' in index_html


# ============================================================================
# PRESETS
# ============================================================================

class TestPresets:
    def test_preset_buttons_exist(self, index_html):
        assert 'data-preset="conservative"' in index_html
        assert 'data-preset="balanced"' in index_html
        assert 'data-preset="aggressive"' in index_html
        assert 'data-preset="growth"' in index_html

    def test_preset_buttons_have_svg_icons(self, index_html):
        match = re.search(r'data-preset="conservative"[^>]*>.*?<svg', index_html, re.DOTALL)
        assert match, "Preset buttons should have SVG icons"


# ============================================================================
# RESPONSIVE DESIGN
# ============================================================================

class TestResponsiveDesign:
    def test_viewport_fit_cover(self, index_html):
        assert 'viewport-fit=cover' in index_html

    def test_apple_mobile_web_app(self, index_html):
        assert 'apple-mobile-web-app-capable' in index_html
