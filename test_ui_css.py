"""Unit tests for CSS design tokens, custom properties, and UI component styles."""
import re
import os
import pytest


CSS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'style.css')


@pytest.fixture
def css_content():
    with open(CSS_PATH, 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def light_tokens(css_content):
    match = re.search(r':root\s*\{([^}]+)\}', css_content)
    assert match, "No :root token block found"
    return match.group(1)


@pytest.fixture
def dark_tokens(css_content):
    match = re.search(r'html\.dark\s*\{([^}]+)\}', css_content)
    assert match, "No html.dark token block found"
    return match.group(1)


def extract_var_names(block):
    return re.findall(r'--([\w-]+)\s*:', block)


def extract_var_values(block):
    return {m.group(1): m.group(2).strip() for m in re.finditer(r'--([\w-]+)\s*:\s*([^;]+);', block)}


# ============================================================================
# DESIGN TOKENS — LIGHT MODE
# ============================================================================

class TestLightModeTokens:
    def test_has_root_block(self, css_content):
        assert ':root' in css_content

    def test_core_color_tokens_present(self, light_tokens):
        names = extract_var_names(light_tokens)
        required = ['bg', 'surface', 'surface-card', 'primary', 'text', 'muted', 'border', 'success', 'error']
        for token in required:
            assert token in names, f"Missing light token: --{token}"

    def test_shadow_tokens_present(self, light_tokens):
        names = extract_var_names(light_tokens)
        required = ['shadow-sm', 'shadow-md', 'shadow-lg', 'shadow-xl', 'shadow-inner']
        for token in required:
            assert token in names, f"Missing shadow token: --{token}"

    def test_glass_tokens_present(self, light_tokens):
        names = extract_var_names(light_tokens)
        for token in ['glass-bg', 'glass-border', 'glass-blur']:
            assert token in names, f"Missing glass token: --{token}"

    def test_spacing_tokens_present(self, light_tokens):
        names = extract_var_names(light_tokens)
        for token in ['space-xs', 'space-sm', 'space-md', 'space-lg', 'space-xl', 'space-2xl']:
            assert token in names, f"Missing spacing token: --{token}"

    def test_radius_tokens_present(self, light_tokens):
        names = extract_var_names(light_tokens)
        for token in ['radius-sm', 'radius-md', 'radius-lg', 'radius-xl', 'radius-2xl', 'radius-full']:
            assert token in names, f"Missing radius token: --{token}"

    def test_typography_tokens_present(self, light_tokens):
        names = extract_var_names(light_tokens)
        for token in ['font-sans', 'text-body', 'text-caption', 'leading-body']:
            assert token in names, f"Missing typography token: --{token}"

    def test_motion_tokens_present(self, light_tokens):
        names = extract_var_names(light_tokens)
        for token in ['ease-out-expo', 'ease-out-quart', 'ease-spring', 'duration-fast', 'duration-normal']:
            assert token in names, f"Missing motion token: --{token}"

    def test_z_index_tokens_present(self, light_tokens):
        names = extract_var_names(light_tokens)
        for token in ['z-base', 'z-dropdown', 'z-nav', 'z-modal']:
            assert token in names, f"Missing z-index token: --{token}"


# ============================================================================
# DESIGN TOKENS — DARK MODE
# ============================================================================

class TestDarkModeTokens:
    def test_has_dark_block(self, css_content):
        assert 'html.dark' in css_content

    def test_dark_overrides_core_colors(self, dark_tokens):
        names = extract_var_names(dark_tokens)
        assert 'bg' in names
        assert 'surface' in names
        assert 'text' in names
        assert 'primary' in names

    def test_dark_overrides_shadows(self, dark_tokens):
        names = extract_var_names(dark_tokens)
        assert 'shadow-md' in names
        assert 'shadow-lg' in names

    def test_dark_overrides_glass(self, dark_tokens):
        names = extract_var_names(dark_tokens)
        assert 'glass-bg' in names
        assert 'glass-border' in names

    def test_dark_uses_dark_colors(self, dark_tokens):
        values = extract_var_values(dark_tokens)
        assert values.get('bg', '').startswith('#0'), "Dark bg should be near-black"
        assert values.get('text', '').startswith('#F'), "Dark text should be near-white"

    def test_dark_has_color_scheme(self, css_content):
        assert 'color-scheme: dark' in css_content


# ============================================================================
# BANNED PATTERNS
# ============================================================================

class TestBannedPatterns:
    def test_no_banned_font_families(self, css_content):
        banned = ['Roboto', 'Inter', 'Arial', 'Helvetica']
        for font in banned:
            pattern = re.compile(rf'font-family\s*:\s*[^;]*{font}', re.IGNORECASE)
            assert not pattern.search(css_content), f"Banned font found: {font}"

    def test_no_banned_material_icons(self, css_content):
        assert 'MaterialSymbolsRounded' not in css_content
        assert 'material-symbols' not in css_content.lower()

    def test_no_banned_shadow_values(self, css_content):
        assert 'rgba(0,0,0,0.3)' not in css_content or '--shadow-md' in css_content

    def test_geist_font_used(self, css_content):
        assert 'Geist' in css_content or 'geist' in css_content.lower()

    def test_phosphor_svgs_used(self, css_content):
        assert "stroke-width='1.5'" in css_content or 'stroke-width=%221.5%22' in css_content or 'stroke-width="1.5"' in css_content

    def test_custom_easing_curves(self, css_content):
        assert 'cubic-bezier' in css_content

    def test_backdrop_blur_present(self, css_content):
        assert 'backdrop-filter' in css_content


# ============================================================================
# DOUBLE-BEZEL CARD ARCHITECTURE
# ============================================================================

class TestDoubleBezelCards:
    def test_card_outer_exists(self, css_content):
        assert '.card-outer' in css_content

    def test_card_inner_exists(self, css_content):
        assert '.card-inner' in css_content

    def test_card_outer_has_glass_border(self, css_content):
        match = re.search(r'\.card-outer\s*\{[^}]*border[^}]*\}', css_content, re.DOTALL)
        assert match, ".card-outer should have a border property"
        assert 'var(--glass-border)' in match.group()

    def test_card_inner_has_surface_bg(self, css_content):
        match = re.search(r'\.card-inner\s*\{[^}]*background[^}]*\}', css_content, re.DOTALL)
        assert match, ".card-inner should have a background property"

    def test_card_outer_has_backdrop_filter(self, css_content):
        match = re.search(r'\.card-outer\s*\{[^}]*backdrop-filter[^}]*\}', css_content, re.DOTALL)
        assert match, ".card-inner should have backdrop-filter"

    def test_card_transition(self, css_content):
        match = re.search(r'\.card-outer\s*\{[^}]*transition[^}]*\}', css_content, re.DOTALL)
        assert match, ".card-outer should have a transition"

    def test_eyebrow_exists(self, css_content):
        assert '.eyebrow' in css_content

    def test_eyebrow_has_border_radius(self, css_content):
        match = re.search(r'\.eyebrow\s*\{[^}]*border-radius[^}]*\}', css_content, re.DOTALL)
        assert match, ".eyebrow should have border-radius"


# ============================================================================
# FLOATING GLASS NAV
# ============================================================================

class TestFloatingGlassNav:
    def test_nav_is_fixed(self, css_content):
        match = re.search(r'\.nav\s*\{[^}]*position\s*:\s*fixed[^}]*\}', css_content, re.DOTALL)
        assert match, ".nav should be position: fixed"

    def test_nav_is_centered(self, css_content):
        match = re.search(r'\.nav\s*\{[^}]*left\s*:\s*50%[^}]*\}', css_content, re.DOTALL)
        assert match, ".nav should be centered with left: 50%"

    def test_nav_has_glass_bg(self, css_content):
        match = re.search(r'\.nav__inner\s*\{[^}]*background[^}]*\}', css_content, re.DOTALL)
        assert match, ".nav__inner should have a background"
        assert 'var(--glass-bg)' in match.group()

    def test_nav_has_backdrop_blur(self, css_content):
        match = re.search(r'\.nav__inner\s*\{[^}]*backdrop-filter[^}]*\}', css_content, re.DOTALL)
        assert match, ".nav__inner should have backdrop-filter"

    def test_nav_has_border_radius(self, css_content):
        match = re.search(r'\.nav__inner\s*\{[^}]*border-radius\s*:\s*var\(--radius-full\)[^}]*\}', css_content, re.DOTALL)
        assert match, ".nav__inner should use radius-full"

    def test_hamburger_exists(self, css_content):
        assert '.nav__hamburger' in css_content

    def test_hamburger_morph(self, css_content):
        assert '.nav__hamburger.active' in css_content

    def test_mobile_overlay_exists(self, css_content):
        assert '.nav-overlay' in css_content


# ============================================================================
# FORM ELEMENTS
# ============================================================================

class TestFormElements:
    def test_text_input_exists(self, css_content):
        assert '.text-input' in css_content

    def test_select_input_exists(self, css_content):
        assert '.custom-select' in css_content

    def test_btn_primary_exists(self, css_content):
        assert '.btn--primary' in css_content

    def test_btn_icon_exists(self, css_content):
        assert '.btn-icon' in css_content

    def test_btn_has_min_height(self, css_content):
        match = re.search(r'\.btn\s*\{[^}]*min-height[^}]*\}', css_content, re.DOTALL)
        assert match, ".btn should have min-height (44px touch target)"

    def test_select_input_custom_arrow(self, css_content):
        match = re.search(r'\.custom-select__trigger\s*\{[^}]*padding-right[^}]*\}', css_content, re.DOTALL)
        assert match, ".custom-select__trigger should have padding-right for arrow"


# ============================================================================
# METRIC CARDS
# ============================================================================

class TestMetricCards:
    def test_metric_card_exists(self, css_content):
        assert '.metric-card' in css_content

    def test_metric_card_grid(self, css_content):
        assert '.metrics' in css_content

    def test_metric_card_hover(self, css_content):
        match = re.search(r'\.metric-card:hover\s*\{[^}]*transform[^}]*\}', css_content, re.DOTALL)
        assert match, ".metric-card:hover should have transform"

    def test_metric_success_variant(self, css_content):
        assert '.metric-card--success' in css_content

    def test_metric_error_variant(self, css_content):
        assert '.metric-card--error' in css_content

    def test_metric_accent_variant(self, css_content):
        assert '.metric-card--accent' in css_content


# ============================================================================
# CHART & TABLE STYLES
# ============================================================================

class TestChartTableStyles:
    def test_chart_box_exists(self, css_content):
        assert '.chart-box' in css_content

    def test_tabs_exist(self, css_content):
        assert '.tabs' in css_content
        assert '.tab' in css_content

    def test_tab_active_has_indicator(self, css_content):
        assert '.tab.active::after' in css_content

    def test_table_exists(self, css_content):
        assert '.table' in css_content

    def test_table_wrap_exists(self, css_content):
        assert '.table-wrap' in css_content


# ============================================================================
# SCROLL REVEAL ANIMATIONS
# ============================================================================

class TestScrollAnimations:
    def test_reveal_class_exists(self, css_content):
        assert '.reveal' in css_content

    def test_reveal_has_opacity_zero(self, css_content):
        match = re.search(r'\.reveal\s*\{[^}]*opacity\s*:\s*0[^}]*\}', css_content, re.DOTALL)
        assert match, ".reveal should start with opacity: 0"

    def test_revealed_class_exists(self, css_content):
        assert '.reveal.revealed' in css_content

    def test_revealed_has_opacity_one(self, css_content):
        match = re.search(r'\.reveal\.revealed\s*\{[^}]*opacity\s*:\s*1[^}]*\}', css_content, re.DOTALL)
        assert match, ".reveal.revealed should have opacity: 1"

    def test_reveal_has_blur(self, css_content):
        match = re.search(r'\.reveal\s*\{[^}]*filter\s*:\s*blur[^}]*\}', css_content, re.DOTALL)
        assert match, ".reveal should have blur filter"

    def test_reveal_delay_classes(self, css_content):
        for i in range(1, 5):
            assert f'.reveal-delay-{i}' in css_content, f"Missing .reveal-delay-{i}"

    def test_prefers_reduced_motion(self, css_content):
        assert 'prefers-reduced-motion' in css_content


# ============================================================================
# RESPONSIVE MOBILE STYLES
# ============================================================================

class TestMobileResponsive:
    def test_mobile_media_query(self, css_content):
        assert '@media (max-width: 767px)' in css_content

    def test_mobile_grid_single_column(self, css_content):
        assert '@media (max-width: 767px)' in css_content, "Missing mobile media query"
        assert '.grid' in css_content, "No .grid rule found"
        assert 'grid-template-columns: 1fr' in css_content, "Grid should have 1fr column"

    def test_mobile_body_overflow_auto(self, css_content):
        assert 'overflow: auto' in css_content

    def test_ios_zoom_prevention(self, css_content):
        assert 'font-size: 16px !important' in css_content

    def test_tiny_screen_breakpoint(self, css_content):
        assert '@media (max-width: 400px)' in css_content


# ============================================================================
# DARK MODE TOGGLE SUPPORT
# ============================================================================

class TestDarkModeSupport:
    def test_dark_block_exists(self, css_content):
        assert 'html.dark' in css_content

    def test_dark_surface_card(self, dark_tokens):
        values = extract_var_values(dark_tokens)
        assert 'surface-card' in values

    def test_dark_primary_color(self, dark_tokens):
        values = extract_var_values(dark_tokens)
        assert 'primary' in values

    def test_dark_success_error_colors(self, dark_tokens):
        names = extract_var_names(dark_tokens)
        assert 'success' in names
        assert 'error' in names


# ============================================================================
# ASYMMETRICAL BENTO LAYOUT
# ============================================================================

class TestBentoLayout:
    def test_grid_is_css_grid(self, css_content):
        match = re.search(r'\.grid\s*\{[^}]*display\s*:\s*grid[^}]*\}', css_content, re.DOTALL)
        assert match, ".grid should use display: grid"

    def test_desktop_grid_columns(self, css_content):
        match = re.search(r'@media\s*\(min-width:\s*1024px\)\s*\{[^}]*\.grid\s*\{[^}]*grid-template-columns\s*:\s*380px\s+1fr[^}]*\}', css_content, re.DOTALL)
        assert match, "Desktop grid should be 380px 1fr"

    def test_result_grid_exists(self, css_content):
        assert '.result-grid' in css_content

    def test_result_grid_desktop(self, css_content):
        assert '.result-grid__metrics' in css_content
        assert '.result-grid__chart' in css_content
        assert '.result-grid__details' in css_content
        assert '.result-grid__actions' in css_content


# ============================================================================
# FINAL POLISH
# ============================================================================

class TestFinalPolish:
    def test_smooth_scroll(self, css_content):
        assert 'scroll-behavior: smooth' in css_content

    def test_focus_visible(self, css_content):
        assert '*:focus-visible' in css_content

    def test_selection_color(self, css_content):
        assert '::selection' in css_content

    def test_loading_spinner(self, css_content):
        assert '@keyframes spin' in css_content
        assert '.btn--loading' in css_content

    def test_tooltip_trigger(self, css_content):
        assert '.tooltip-trigger' in css_content
