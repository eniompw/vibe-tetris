import pygame
import random

pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
RED = (255, 0, 0)

COLORS = [CYAN, BLUE, ORANGE, YELLOW, GREEN, PURPLE, RED]

# Screen dimensions
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
PANEL_WIDTH = 7  # width of the side panel in blocks
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + PANEL_WIDTH)
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
GRID_PIXEL_WIDTH = BLOCK_SIZE * GRID_WIDTH

# Tetromino shapes (1 represents block, 0 represents empty)
SHAPES = [
    [[1, 1, 1, 1]],         # I
    [[1, 0, 0], [1, 1, 1]], # J
    [[0, 0, 1], [1, 1, 1]], # L
    [[1, 1], [1, 1]],       # O
    [[0, 1, 1], [1, 1, 0]], # S
    [[0, 1, 0], [1, 1, 1]], # T
    [[1, 1, 0], [0, 1, 1]]  # Z
]

# Wall kick offsets to try when rotation fails
WALL_KICKS = [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0), (0, -1), (0, -2)]

# Font setup
FONT_NAME = "segoeuiemoji"
FALLBACK_FONTS = ["segoeui", "arial", "calibri", "verdana", None]


def get_font(size, bold=False):
    """Try preferred fonts, then fall back to default."""
    for name in [FONT_NAME] + FALLBACK_FONTS:
        try:
            f = pygame.font.SysFont(name, size, bold)
            return f
        except Exception:
            continue
    return pygame.font.Font(None, size)


class Tetromino:
    def __init__(self, shape_idx=None):
        self.x = GRID_WIDTH // 2 - 1
        self.y = 0
        if shape_idx is None:
            self.shape_idx = random.randint(0, len(SHAPES) - 1)
        else:
            self.shape_idx = shape_idx
        self.shape = [row[:] for row in SHAPES[self.shape_idx]]
        self.color = COLORS[self.shape_idx]

    def get_rotated_shape(self):
        """Rotate matrix 90 degrees clockwise."""
        rotated = []
        for c in range(len(self.shape[0])):
            new_row = []
            for r in range(len(self.shape) - 1, -1, -1):
                new_row.append(self.shape[r][c])
            rotated.append(new_row)
        return rotated


class TetrisApp:
    def __init__(self):
        self.fullscreen = False
        self.windowed = True  # True when in normal windowed mode (not maximized/fullscreen)
        self.game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.draw_target = self.screen  # surface all drawing goes to
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()
        self.init_game()

    def init_game(self):
        self.grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.held_piece = None
        self.can_hold = True  # can only hold once per drop
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False
        self.paused = False
        self.fall_time = 0
        self.fall_speed = 500  # ms between automatic drops
        # Line clear animation state
        self.clearing_rows = []      # rows currently animating
        self.clear_flash_timer = 0
        self.clear_flash_duration = 300  # ms for flash animation
        self.clear_flash_on = True

    def new_piece(self):
        return Tetromino()

    def get_fall_speed(self):
        """Calculate fall speed based on level."""
        return max(100, 500 - (self.level - 1) * 40)

    # ─── Drawing ──────────────────────────────────────────

    def toggle_fullscreen(self):
        """Toggle between windowed and fullscreen mode."""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.windowed = not self.fullscreen

    def _needs_scaling(self):
        """Check if the screen size differs from the native game size."""
        sw, sh = self.screen.get_size()
        return sw != SCREEN_WIDTH or sh != SCREEN_HEIGHT

    def draw_block(self, screen_x, screen_y, color, is_grid=False, ghost=False):
        if color == BLACK:
            if is_grid:
                pygame.draw.rect(self.draw_target, DARK_GRAY,
                                 [screen_x, screen_y, BLOCK_SIZE, BLOCK_SIZE], 1)
            return

        if ghost:
            # Draw ghost piece as an outline only
            pygame.draw.rect(self.draw_target, color,
                             [screen_x + 2, screen_y + 2, BLOCK_SIZE - 4, BLOCK_SIZE - 4], 2)
            return

        # Filled block with 3D bevel effect
        pygame.draw.rect(self.draw_target, color,
                         [screen_x, screen_y, BLOCK_SIZE, BLOCK_SIZE], 0)

        r, g, b = color
        light = (min(255, int(r * 1.5) + 50), min(255, int(g * 1.5) + 50), min(255, int(b * 1.5) + 50))
        dark = (int(r * 0.5), int(g * 0.5), int(b * 0.5))

        t = 4  # bevel thickness

        # Top highlight
        pygame.draw.polygon(self.draw_target, light, [
            (screen_x, screen_y),
            (screen_x + BLOCK_SIZE, screen_y),
            (screen_x + BLOCK_SIZE - t, screen_y + t),
            (screen_x + t, screen_y + t)
        ])
        # Left highlight
        pygame.draw.polygon(self.draw_target, light, [
            (screen_x, screen_y),
            (screen_x + t, screen_y + t),
            (screen_x + t, screen_y + BLOCK_SIZE - t),
            (screen_x, screen_y + BLOCK_SIZE)
        ])
        # Bottom shadow
        pygame.draw.polygon(self.draw_target, dark, [
            (screen_x, screen_y + BLOCK_SIZE),
            (screen_x + t, screen_y + BLOCK_SIZE - t),
            (screen_x + BLOCK_SIZE - t, screen_y + BLOCK_SIZE - t),
            (screen_x + BLOCK_SIZE, screen_y + BLOCK_SIZE)
        ])
        # Right shadow
        pygame.draw.polygon(self.draw_target, dark, [
            (screen_x + BLOCK_SIZE, screen_y),
            (screen_x + BLOCK_SIZE, screen_y + BLOCK_SIZE),
            (screen_x + BLOCK_SIZE - t, screen_y + BLOCK_SIZE - t),
            (screen_x + BLOCK_SIZE - t, screen_y + t)
        ])

        # Inner fill
        pygame.draw.rect(self.draw_target, color,
                         [screen_x + t, screen_y + t, BLOCK_SIZE - 2 * t, BLOCK_SIZE - 2 * t], 0)
        # Outer border
        pygame.draw.rect(self.draw_target, BLACK,
                         [screen_x, screen_y, BLOCK_SIZE, BLOCK_SIZE], 1)

    def draw_grid(self):
        for y in range(GRID_HEIGHT):
            # If this row is in the flash animation, alternate white/normal
            if y in self.clearing_rows:
                if self.clear_flash_on:
                    for x in range(GRID_WIDTH):
                        pygame.draw.rect(self.draw_target, WHITE,
                                         [x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE])
                    continue
            for x in range(GRID_WIDTH):
                self.draw_block(x * BLOCK_SIZE, y * BLOCK_SIZE, self.grid[y][x], is_grid=True)

        # Grid border
        pygame.draw.rect(self.draw_target, GRAY,
                         [0, 0, GRID_PIXEL_WIDTH, SCREEN_HEIGHT], 2)

    def draw_piece(self, piece):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    screen_x = (piece.x + x) * BLOCK_SIZE
                    screen_y = (piece.y + y) * BLOCK_SIZE
                    if piece.y + y >= 0:
                        self.draw_block(screen_x, screen_y, piece.color)

    def draw_ghost_piece(self):
        """Draw a ghost/shadow showing where the piece will land."""
        ghost_y = self.current_piece.y
        while True:
            ghost_y += 1
            valid = True
            for y, row in enumerate(self.current_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        gy = ghost_y + y
                        gx = self.current_piece.x + x
                        if gx < 0 or gx >= GRID_WIDTH or gy >= GRID_HEIGHT:
                            valid = False
                        elif gy >= 0 and self.grid[gy][gx] != BLACK:
                            valid = False
            if not valid:
                ghost_y -= 1
                break

        if ghost_y != self.current_piece.y:
            for y, row in enumerate(self.current_piece.shape):
                for x, cell in enumerate(row):
                    if cell and ghost_y + y >= 0:
                        screen_x = (self.current_piece.x + x) * BLOCK_SIZE
                        screen_y = (ghost_y + y) * BLOCK_SIZE
                        self.draw_block(screen_x, screen_y, self.current_piece.color, ghost=True)

    def draw_mini_piece(self, piece_or_idx, start_x, start_y):
        """Draw a small preview of a piece (for Hold / Next display)."""
        if piece_or_idx is None:
            return
        if isinstance(piece_or_idx, Tetromino):
            shape = SHAPES[piece_or_idx.shape_idx]
            color = piece_or_idx.color
        else:
            shape = SHAPES[piece_or_idx]
            color = COLORS[piece_or_idx]

        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    sx = start_x + x * BLOCK_SIZE
                    sy = start_y + y * BLOCK_SIZE
                    self.draw_block(sx, sy, color)

    def draw_ui(self):
        panel_x = GRID_PIXEL_WIDTH + 12  # left edge of panel text
        panel_w = PANEL_WIDTH * BLOCK_SIZE - 4
        font_lg = get_font(22, bold=True)
        font_md = get_font(18, bold=True)
        font_sm = get_font(14)

        # ── Hold ──
        label = font_lg.render("HOLD", True, WHITE)
        self.draw_target.blit(label, (panel_x, 10))
        # Box
        box_x = panel_x
        box_y = 38
        box_w = 4 * BLOCK_SIZE + 10
        box_h = 3 * BLOCK_SIZE + 6
        pygame.draw.rect(self.draw_target, DARK_GRAY, [box_x, box_y, box_w, box_h])
        pygame.draw.rect(self.draw_target, GRAY, [box_x, box_y, box_w, box_h], 1)
        if self.held_piece is not None:
            self.draw_mini_piece(self.held_piece, box_x + 5, box_y + 5)

        # ── Next ──
        next_y = box_y + box_h + 14
        label = font_lg.render("NEXT", True, WHITE)
        self.draw_target.blit(label, (panel_x, next_y))
        nbox_y = next_y + 28
        pygame.draw.rect(self.draw_target, DARK_GRAY, [box_x, nbox_y, box_w, box_h])
        pygame.draw.rect(self.draw_target, GRAY, [box_x, nbox_y, box_w, box_h], 1)
        self.draw_mini_piece(self.next_piece, box_x + 5, nbox_y + 5)

        # ── Score / Level / Lines ──
        stats_y = nbox_y + box_h + 18
        for i, (lbl, val) in enumerate([("SCORE", self.score), ("LEVEL", self.level), ("LINES", self.lines_cleared)]):
            y_off = stats_y + i * 44
            t = font_md.render(lbl, True, GRAY)
            self.draw_target.blit(t, (panel_x, y_off))
            v = font_lg.render(str(val), True, WHITE)
            self.draw_target.blit(v, (panel_x, y_off + 20))

        # ── Controls ──
        ctrl_y = stats_y + 3 * 44 + 10
        pygame.draw.line(self.draw_target, GRAY, (panel_x, ctrl_y), (panel_x + panel_w - 10, ctrl_y))
        ctrl_y += 6
        controls = [
            "← →   Move",
            "↑       Rotate",
            "↓       Soft Drop",
            "Space  Hard Drop",
            "C       Hold",
            "P       Pause",
            "F11    Fullscreen",
        ]
        for i, line in enumerate(controls):
            t = font_sm.render(line, True, GRAY)
            self.draw_target.blit(t, (panel_x, ctrl_y + i * 20))

        # ── Overlays ──
        if self.paused and not self.game_over:
            overlay = pygame.Surface((GRID_PIXEL_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.draw_target.blit(overlay, (0, 0))
            pause_font = get_font(48, bold=True)
            txt = pause_font.render("PAUSED", True, WHITE)
            rect = txt.get_rect(center=(GRID_PIXEL_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.draw_target.blit(txt, rect)

        if self.game_over:
            overlay = pygame.Surface((GRID_PIXEL_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 170))
            self.draw_target.blit(overlay, (0, 0))
            go_font = get_font(40, bold=True)
            go_text = go_font.render("GAME OVER", True, RED)
            rect = go_text.get_rect(center=(GRID_PIXEL_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            self.draw_target.blit(go_text, rect)

            r_font = get_font(25, bold=True)
            r_text = r_font.render("Press 'R' to Restart", True, WHITE)
            r_rect = r_text.get_rect(center=(GRID_PIXEL_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.draw_target.blit(r_text, r_rect)

    # ─── Game Logic ──────────────────────────────────────

    def valid_space(self, piece, shape=None):
        if shape is None:
            shape = piece.shape
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    gy = piece.y + y
                    gx = piece.x + x
                    if gx < 0 or gx >= GRID_WIDTH or gy >= GRID_HEIGHT:
                        return False
                    if gy >= 0 and self.grid[gy][gx] != BLACK:
                        return False
        return True

    def try_rotate(self):
        """Try rotation with wall kicks."""
        rotated = self.current_piece.get_rotated_shape()
        original_x = self.current_piece.x
        original_y = self.current_piece.y

        for dx, dy in WALL_KICKS:
            self.current_piece.x = original_x + dx
            self.current_piece.y = original_y + dy
            if self.valid_space(self.current_piece, rotated):
                self.current_piece.shape = rotated
                return True
            self.current_piece.x = original_x
            self.current_piece.y = original_y

        return False

    def lock_piece(self, piece):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    if piece.y + y >= 0:
                        self.grid[piece.y + y][piece.x + x] = piece.color

        self.can_hold = True  # reset hold lock
        self.start_clear_rows()

    def start_clear_rows(self):
        """Find full rows and start the flash animation."""
        full_rows = []
        for y in range(GRID_HEIGHT):
            if BLACK not in self.grid[y]:
                full_rows.append(y)

        if full_rows:
            self.clearing_rows = full_rows
            self.clear_flash_timer = self.clear_flash_duration
            self.clear_flash_on = True
        else:
            # No rows to clear, spawn next piece immediately
            self.spawn_next_piece()

    def finish_clear_rows(self):
        """Actually remove the cleared rows after animation finishes."""
        cleared = len(self.clearing_rows)
        for y in sorted(self.clearing_rows):
            del self.grid[y]
            self.grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
            # Adjust remaining row indices since we shifted the grid
            self.clearing_rows = [r if r < y else r for r in self.clearing_rows]

        self.clearing_rows = []

        if cleared > 0:
            # Standard Tetris scoring: single/double/triple/tetris × level
            scores = {1: 100, 2: 300, 3: 500, 4: 800}
            self.score += scores.get(cleared, 800) * self.level
            self.lines_cleared += cleared
            # Level up every 10 lines
            self.level = self.lines_cleared // 10 + 1
            self.fall_speed = self.get_fall_speed()

        self.spawn_next_piece()

    def spawn_next_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        if not self.valid_space(self.current_piece):
            self.game_over = True

    def hold_piece(self):
        """Swap current piece with held piece. Only once per drop."""
        if not self.can_hold:
            return

        self.can_hold = False
        current_idx = self.current_piece.shape_idx

        if self.held_piece is not None:
            # Swap: create a new piece with the held shape
            self.current_piece = Tetromino(self.held_piece.shape_idx)
            self.held_piece = Tetromino(current_idx)
        else:
            self.held_piece = Tetromino(current_idx)
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()

    def hard_drop(self):
        """Drop piece instantly, awarding 2 points per cell dropped."""
        cells_dropped = 0
        while self.valid_space(self.current_piece):
            self.current_piece.y += 1
            cells_dropped += 1
        self.current_piece.y -= 1
        cells_dropped -= 1
        self.score += cells_dropped * 2
        self.lock_piece(self.current_piece)

    def soft_drop(self):
        """Move piece down one row, awarding 1 point."""
        self.current_piece.y += 1
        if not self.valid_space(self.current_piece):
            self.current_piece.y -= 1
        else:
            self.score += 1

    # ─── Main Loop ────────────────────────────────────────

    def run(self):
        running = True
        while running:
            # Set draw_target: when scaled we draw to game_surface first, then scale
            needs_scale = self._needs_scaling()
            if needs_scale:
                self.draw_target = self.game_surface
            else:
                self.draw_target = self.screen

            self.draw_target.fill(BLACK)
            time_delta = self.clock.tick(60)

            # ── Line-clear animation update ──
            if self.clearing_rows:
                self.clear_flash_timer -= time_delta
                # Toggle flash every 60ms
                flash_phase = self.clear_flash_timer // 60
                self.clear_flash_on = (flash_phase % 2 == 0)
                if self.clear_flash_timer <= 0:
                    self.finish_clear_rows()

            # ── Automatic fall ──
            if not self.game_over and not self.paused and not self.clearing_rows:
                self.fall_time += time_delta
                if self.fall_time > self.fall_speed:
                    self.current_piece.y += 1
                    if not self.valid_space(self.current_piece):
                        self.current_piece.y -= 1
                        self.lock_piece(self.current_piece)
                    self.fall_time = 0

            # ── Input handling ──
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.VIDEORESIZE and not self.fullscreen:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.windowed = (event.w == SCREEN_WIDTH and event.h == SCREEN_HEIGHT)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        self.toggle_fullscreen()
                    elif self.game_over:
                        if event.key == pygame.K_r:
                            self.init_game()
                    elif event.key in (pygame.K_p, pygame.K_ESCAPE):
                        self.paused = not self.paused
                    elif not self.paused and not self.clearing_rows:
                        if event.key == pygame.K_LEFT:
                            self.current_piece.x -= 1
                            if not self.valid_space(self.current_piece):
                                self.current_piece.x += 1
                        elif event.key == pygame.K_RIGHT:
                            self.current_piece.x += 1
                            if not self.valid_space(self.current_piece):
                                self.current_piece.x -= 1
                        elif event.key == pygame.K_DOWN:
                            self.soft_drop()
                        elif event.key == pygame.K_UP:
                            self.try_rotate()
                        elif event.key == pygame.K_SPACE:
                            self.hard_drop()
                        elif event.key == pygame.K_c:
                            self.hold_piece()

            # ── Drawing ──
            self.draw_grid()
            if not self.game_over and not self.paused:
                self.draw_ghost_piece()
                self.draw_piece(self.current_piece)
            elif not self.game_over:
                # While paused, still show the piece (ghost hidden)
                self.draw_piece(self.current_piece)

            self.draw_ui()

            # ── Present to screen ──
            if needs_scale:
                # Scale game_surface to fit the screen, preferring integer multiples
                self.screen.fill(BLACK)
                sw, sh = self.screen.get_size()
                # Find the largest integer scale that fits
                int_scale = max(1, min(sw // SCREEN_WIDTH, sh // SCREEN_HEIGHT))
                new_w = SCREEN_WIDTH * int_scale
                new_h = SCREEN_HEIGHT * int_scale
                # If integer scale is too small (<50% of screen), use fractional smoothscale
                if new_w < sw * 0.5 or new_h < sh * 0.5:
                    frac_scale = min(sw / SCREEN_WIDTH, sh / SCREEN_HEIGHT)
                    new_w = int(SCREEN_WIDTH * frac_scale)
                    new_h = int(SCREEN_HEIGHT * frac_scale)
                    scaled = pygame.transform.smoothscale(self.game_surface, (new_w, new_h))
                else:
                    scaled = pygame.transform.scale(self.game_surface, (new_w, new_h))
                x_off = (sw - new_w) // 2
                y_off = (sh - new_h) // 2
                self.screen.blit(scaled, (x_off, y_off))

            pygame.display.flip()

        pygame.quit()


if __name__ == '__main__':
    app = TetrisApp()
    app.run()
