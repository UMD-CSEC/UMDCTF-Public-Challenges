#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <ctype.h>
#include "nwl.c"

// #define fail(x, ...) printf("%3d: " x "\n", __LINE__, ##__VA_ARGS__)
#define fail(x, ...) printf(x "\n", ##__VA_ARGS__)
#define RAND_MOD(x) ((uint64_t)rand() * (uint64_t)(x)) / (((uint64_t)RAND_MAX) + 1)

const size_t NUM_WORDS = sizeof(wordlist) / sizeof(wordlist[0]);

bool check_word(const char* word) {
	size_t low = 0;
	size_t high = NUM_WORDS;

	size_t length = strlen(word);

	while (low < high) {
		size_t mid = (high - low) / 2 + low;
		size_t mid_length = strlen(wordlist[mid]);
		if (mid_length < length) {
			low = mid + 1;
			continue;
		} else if (mid_length > length) {
			high = mid;
			continue;
		}
		int cmp = strncasecmp(wordlist[mid], word, length);
		if (cmp < 0) {
			low = mid + 1;
		} else if (cmp > 0) {
			high = mid;
		} else {
			return true;
		}
	}
	return low < NUM_WORDS && strcasecmp(wordlist[low], word) == 0;
}

void shuffle(char* arr, size_t length) {
	// fisher yates shuffle, i think
	for (size_t i = 0; i < length - 1; i++) {
		size_t j = i + RAND_MOD(length-i);
		char tmp = arr[i];
		arr[i] = arr[j];
		arr[j] = tmp;
	}
}

void sort(char* arr, size_t length) {
	// selection sort idc
	for (size_t i = 0; i + 1 < length; i++) {
		uint8_t lowest = 0x7f;
		size_t lowest_position = 0;
		for (size_t j = i; j < length; j++) {
			if ((uint8_t) arr[j] <= lowest) {
				lowest = (uint8_t)arr[j];
				lowest_position = j;
			}
		}
		arr[lowest_position] = (uint8_t) arr[i];
		arr[i] = lowest;
	}
}

void play() {
	char input[16];
	char board[15][15];
	memset(board, '.', 225);
	board[7][7] = '*';

	char rack_1[8] = {0}, rack_2[8] = {0};

	uint16_t bitmap[15] = {0};

	char tiles[101] = "AAAAAAAAABBCCDDDDEEEEEEEEEEEEFFGGGHHIIIIIIIIIJKLLLLMMNNNNNNOOOOOOOOPPQRRRRRRSSSSTTTTTTUUUUVVWWXYYZ__";
	uint8_t n_tiles = 100;

	shuffle(tiles, n_tiles);

	n_tiles -= 7; memcpy(rack_1, tiles + n_tiles, 7);
	n_tiles -= 7; memcpy(rack_2, tiles + n_tiles, 7);

	while (1) {
read_command:
		// print board
		puts("   A B C D E F G H I J K L M N O");
		for (int i = 0; i < 15; i++) {
			printf("%2d", i + 1);
			for (int j = 0; j < 15; j++) {
				putchar(' ');
				putchar(board[i][j]);
			}
			putchar('\n');
		}

		// sort rack
		size_t rack_1_len = strlen(rack_1);
		sort(rack_1, rack_1_len);

		printf("rack: %s\n", rack_1);
		scanf("%10s", input);
		if (strcmp(input, "pass") == 0) {
			puts("you passed your turn");
		} else if (strcmp(input, "resign") == 0) {
			puts("you lose");
			break;
		} else if (strcmp(input, "exchange") == 0) {
			scanf(" %7s", input);
			size_t n_letters = strlen(input);
			for (size_t i = 0; i < n_letters; i++) {
				input[i] = toupper(input[i]);
			}

			// uses letters from rack
			sort(input, n_letters);
			uint8_t rack_mask = 0;
			for (uint8_t i = 0, j = 0; i < n_letters; i++) {
				char c = input[i];
				while (j < rack_1_len) {
					if (rack_1[j] == c) {
						rack_mask |= 1 << j;
						break;
					}
					j++;
				}
				if (j >= rack_1_len) {
					fail("invalid exchange"); goto read_command;
				}
				j++;
			}

			if (n_tiles == 0) {
				fail("bag is empty"); goto read_command;
			}

			// replenish tiles
			for (uint8_t i = 0; i < rack_1_len; i++) {
				if ((rack_mask >> i) & 1) {
					rack_1[i] = '~';
				}
			}
			sort(rack_1, rack_1_len);

			// draw new tiles from bag
			memcpy(rack_1 + rack_1_len - n_letters, tiles + n_tiles - n_letters, n_letters);
			n_tiles -= n_letters;

			// throw exchanged tiles back into bag
			for (uint8_t i = 0; i < n_letters; i++) {
				uint8_t pos = RAND_MOD(n_tiles + 1);
				tiles[n_tiles] = tiles[pos];
				tiles[pos] = input[i];
				n_tiles += 1;
			}
		} else if (strcmp(input, "move") == 0) {
			int row, col;
			bool along_row = false;
			scanf(" %3s", input); // location
			size_t length = strlen(input);

			input[0] = toupper(input[0]);
			input[1] = toupper(input[1]);
			input[2] = toupper(input[2]);
			if ('A' <= input[0] && input[0] < ('A' + 15)) {
				// down column
				col = input[0] - 'A';
				row = atoi(&input[1]) - 1;
			} else if ('1' <= input[0] && input[0] <= '9') {
				// across row
				col = input[length - 1] - 'A';
				input[length - 1] = 0;
				row = atoi(input) - 1;
				along_row = true;
			} else {
				fail("invalid move"); goto read_command;
			}

			// starting square is on the board
			if (col < 0 || col >= 15 || row < 0 || row >= 15) {
				fail("invalid move"); goto read_command;
			}

			scanf(" %15s", input); // word
			length = strlen(input);

			// word fits on board
			if (along_row && col + length > 15 || !along_row && row + length > 15) {
				fail("invalid move"); goto read_command;
			}

			int rr = row, cc = col;
			uint8_t new_tile_count = 0;
			bool connected = false;
			char new_letters[7] = {0};
			char word[16];
			for (size_t i = 0; i < length; i++) {
				if (rr == 7 && cc == 7) connected = true; // center star
				if ((bitmap[rr] >> cc) & 1) {
					if (input[i] != board[rr][cc]) { // conflict
						fail("invalid move"); goto read_command;
					}
					connected = true;
				} else {
					// new tile
					if (new_tile_count < 7) {
						new_letters[new_tile_count] = input[i];
					}
					new_tile_count++;

					uint8_t word_start, word_end;
					if (along_row) {
						word_start = rr;
						word_end = rr + 1;
					} else {
						word_start = cc;
						word_end = cc + 1;
					}

					if (cc > 0 && ((bitmap[rr]>>(cc-1))&1)) { // left
						if (!along_row) {
							while ((bitmap[rr]>>(word_start-1))&1) {
								word_start--;
								if (word_start == 0) break;
							}
						}
						connected = true;
					}
					if (cc < 14 && (bitmap[rr]>>(cc+1))&1) { // right
						if (!along_row) {
							while ((bitmap[rr]>>word_end)&1) {
								word_end++;
								if (word_end == 15) break;
							}
						}
						connected = true;
					}
					if (rr > 0 && ((bitmap[rr-1]>>cc)&1)) { // top
						if (along_row) {
							while ((bitmap[word_start-1]>>cc)&1) {
								word_start--;
								if (word_start == 0) break;
							}
						}
						connected = true;
					}
					if (rr < 14 && ((bitmap[rr+1]>>cc)&1)) { // bottom
						if (along_row) {
							while ((bitmap[word_end]>>cc)&1) {
								word_end++;
								if (word_end == 15) break;
							}
						}
						connected = true;
					}

					// check overlapping words
					if (word_start + 1 < word_end) {
						for (uint8_t j = word_start; j < word_end; j++) {
							if (along_row && j == rr || !along_row && j == cc) {
								word[j - word_start] = input[i];
							} else {
								word[j - word_start] = along_row ? board[j][cc] : board[rr][j];
							}
						}
						word[word_end - word_start] = 0;
						if (!check_word(word)) {
							fail("invalid word"); goto read_command;
						}
					}
				}
				if (along_row) cc += 1;
				else rr += 1;
			}
			if (!connected) {
				fail("invalid move"); goto read_command;
			}
			if (new_tile_count > rack_1_len) {
				fail("invalid move"); goto read_command;
			}

			// check main word
			uint8_t word_start, word_end;
			if (along_row) {
				word_start = col;
				word_end = col + length;
				while (word_start > 0 && ((bitmap[row]>>(word_start - 1))&1)) word_start--;
				while (word_end < 15 && ((bitmap[row]>>word_end)&1)) word_end++;
			} else {
				word_start = row;
				word_end = row + length;
				while (word_start > 0 && ((bitmap[word_start-1]>>col)&1)) word_start--;
				while (word_end < 15 && ((bitmap[word_end]>>col)&1)) word_end++;
			}
			for (uint8_t j = word_start; j < word_end; j++) {
				if (along_row && j >= col && j < col + length || !along_row && j >= row && j < row + length) {
					word[j - word_start] = input[j - (along_row ? col : row)];
				} else {
					word[j - word_start] = along_row ? board[rr][j] : board[j][cc];
				}
			}
			word[word_end - word_start] = 0;
			if (!check_word(word)) {
				fail("invalid word"); goto read_command;
			}

			// uses letters from rack
			sort(new_letters, new_tile_count);
			uint8_t rack_mask = 0;
			for (uint8_t i = 0, j = 0; i < new_tile_count; i++) {
				char c = new_letters[i];
				if (c >= 'a') c = '_';
				while (j < rack_1_len) {
					if (rack_1[j] == c) {
						rack_mask |= 1 << j;
						break;
					}
					j++;
				}
				if (j >= rack_1_len) {
					fail("invalid move"); goto read_command;
				}
				j++;
			}

			// ok FINALLY place the word on the board
			rr = row, cc = col;
			for (size_t i = 0; i < length; i++) {
				if (!((bitmap[rr] >> cc) & 1)) {
					board[rr][cc] = input[i];
					bitmap[rr] |= 1 << cc;
				}
				if (along_row) cc += 1;
				else rr += 1;
			}

			// replenish tiles
			for (uint8_t i = 0; i < rack_1_len; i++) {
				if ((rack_mask >> i) & 1) {
					rack_1[i] = '~';
				}
			}
			sort(rack_1, rack_1_len);
			if (n_tiles >= new_tile_count) {
				n_tiles -= new_tile_count;
				memcpy(rack_1 + rack_1_len - new_tile_count, tiles + n_tiles, new_tile_count);
			} else {
				memcpy(rack_1 + rack_1_len - new_tile_count, tiles, n_tiles);
				rack_1[rack_1_len - new_tile_count + n_tiles] = 0;
				n_tiles = 0;
			}
		} else {
			fail("invalid command"); goto read_command;
		}

		// out of tiles
		if (rack_1[0] == 0) {
			puts("game over!");
			break;
		}

		// extremely advanced scrabble ai
		puts("your opponent passes their turn");
	}
}

int main() {
	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);
	srand(time(NULL)); // TODO: better seed?

	char choice[2];

	while (1) {
		play();
		puts("play again? (y/n)");
		if (getchar() != 'y') {
			puts("goodbye!");
			break;
		}
		getchar(); // consume newline
	}
	return 0;
}
