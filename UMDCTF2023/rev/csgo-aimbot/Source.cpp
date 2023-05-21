#include <iostream>
#include <Windows.h>
#include <TlHelp32.h>

#define CSGO_WINDOW_NAME "Counter-Strike: Global Offensive - Direct3D 9"
#define dwLocalPlayer 0xDEA964 //Pay attention to these offsets! They might change with game updates...
#define dwEntityList 0x4DFFEF4
#define dwViewMatrix 0x4DF0D24
#define m_dwBoneMatrix 0x26A8
#define m_iTeamNum 0xF4
#define m_iHealth 0x100
#define m_vecOrigin 0x138
#define m_bDormant 0xED

const int SCREEN_WIDTH = GetSystemMetrics(SM_CXSCREEN); 
const int SCREEN_HEIGHT = GetSystemMetrics(SM_CYSCREEN); 

HWND hwnd;
DWORD procId; 
HANDLE hProcess; 
uintptr_t moduleBase; 
HDC hdc;

uintptr_t GetModuleBaseAddress(const char* modName) {
	HANDLE hSnap = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, procId);
	if (hSnap != INVALID_HANDLE_VALUE) {
		MODULEENTRY32 modEntry;
		modEntry.dwSize = sizeof(modEntry);
		if (Module32First(hSnap, &modEntry)) {
			do {
				if (!strcmp(modEntry.szModule, modName)) {
					CloseHandle(hSnap);
					return (uintptr_t)modEntry.modBaseAddr;
				}
			} while (Module32Next(hSnap, &modEntry));
		}
	}
}

template<typename T> T RPM(SIZE_T address) {
	T buffer;
	ReadProcessMemory(hProcess, (LPCVOID)address, &buffer, sizeof(T), NULL);
	return buffer;
}

class Vector3 {
public:
	float x, y, z;
	Vector3() : x(0.f), y(0.f), z(0.f) {}
	Vector3(float _x, float _y, float _z) : x(_x), y(_y), z(_z) {}
};

uintptr_t GetLocalPlayer() {
	return RPM< uintptr_t>(moduleBase + dwLocalPlayer);
}

uintptr_t GetPlayer(int index) {  //Each player has an index. 1-64
	return RPM< uintptr_t>(moduleBase + dwEntityList + index * 0x10); //We multiply the index by 0x10 to select the player we want in the entity list.
}

int GetPlayerHealth(uintptr_t player) { 
	return RPM<int>(player + m_iHealth);
}

Vector3 PlayerLocation(uintptr_t player) { //Stores XYZ coordinates in a Vector3.
	return RPM<Vector3>(player + m_vecOrigin);
}

Vector3 get_head(uintptr_t player) { 
	struct boneMatrix_t {
		byte pad3[12];
		float x;
		byte pad1[12];
		float y;
		byte pad2[12];
		float z;
	};
	uintptr_t boneBase = RPM<uintptr_t>(player + m_dwBoneMatrix);
	boneMatrix_t boneMatrix = RPM<boneMatrix_t>(boneBase + (sizeof(boneMatrix) * 8)); 
	return Vector3(boneMatrix.x, boneMatrix.y, boneMatrix.z);
}

struct view_matrix_t {
	float matrix[16]; 
} vm;

struct Vector3 WorldToScreen(const struct Vector3 pos, struct view_matrix_t matrix) { //This turns 3D coordinates (ex: XYZ) int 2D coordinates (ex: XY).
	struct Vector3 out;
	float _x = matrix.matrix[0] * pos.x + matrix.matrix[1] * pos.y + matrix.matrix[2] * pos.z + matrix.matrix[3];
	float _y = matrix.matrix[4] * pos.x + matrix.matrix[5] * pos.y + matrix.matrix[6] * pos.z + matrix.matrix[7];
	out.z = matrix.matrix[12] * pos.x + matrix.matrix[13] * pos.y + matrix.matrix[14] * pos.z + matrix.matrix[15];

	_x *= 1.f / out.z;
	_y *= 1.f / out.z;

	out.x = SCREEN_WIDTH * .5f; 
	out.y = SCREEN_HEIGHT * .5f;

	out.x += 0.5f * _x * SCREEN_WIDTH + 0.5f;
	out.y -= 0.5f * _y * SCREEN_HEIGHT - 30.0f;

	return out;
}

void Shoot() {
	mouse_event(MOUSEEVENTF_LEFTDOWN, NULL, NULL, 0, 0);
	mouse_event(MOUSEEVENTF_LEFTUP, NULL, NULL, 0, 0);
}

const Vector3 targets[] = {
	Vector3(0, 600, 200), //V
	Vector3(0, -40, -50),
	Vector3(0, -40, -50),
	Vector3(0, -40, -50),
	Vector3(0, -40, 50),
	Vector3(0, -40, 50),
	Vector3(0, -40, 50),

	
	Vector3(0, 600, 0), //A
	Vector3(0, -40, -50),
	Vector3(0, -40, -50),
	Vector3(0, -40, -50),
	Vector3(0, 40, 50),
	Vector3(0, 40, 50),
	Vector3(0, 40, 50),
	Vector3(0, 40, -50),
	Vector3(0, 40, -50),
	Vector3(0, 40, -50),
	Vector3(0, -40, 50),
	Vector3(0, -70, 0),
	Vector3(0, 70, 0),
	Vector3(0, -40, 50),

	Vector3(0, 20, 30), //C
	Vector3(0, 40, 0),
	Vector3(0, 40, 0),
	Vector3(0, 40, 0),
	Vector3(0, 0, -50),
	Vector3(0, 0, -50),
	Vector3(0, 0, -50),
	Vector3(0, 0, -50),
	Vector3(0, -40, 0),
	Vector3(0, -40, 0),
	Vector3(0, -40, 0),

	
	Vector3(0, 100, 0), //B
	Vector3(0, 0, -50),
	Vector3(0, 0, -50),
	Vector3(0, 0, -50),
	Vector3(0, 0, -50),
	Vector3(0, 40, 0),
	Vector3(0, 40, 0),
	Vector3(0, 40, 0),
	Vector3(0, 0, 50),
	Vector3(0, 0, 50),
	Vector3(0, -60, 0),
	Vector3(0, 60, 0),
	Vector3(0, 0, 50),
	Vector3(0, 0, 50),
	Vector3(0, -40, 0),
	Vector3(0, -40, 0),
	Vector3(0, -40, 0),

	Vector3(0, 80, 0), //A
	Vector3(0, -40, -50),
	Vector3(0, -40, -50),
	Vector3(0, -40, -50),
	Vector3(0, 40, 50),
	Vector3(0, 40, 50),
	Vector3(0, 40, 50),
	Vector3(0, 40, 50),
	Vector3(0, 40, -50),
	Vector3(0, 40, -50),
	Vector3(0, 40, -50),
	Vector3(0, -40, 50),
	Vector3(0, -70, 0),
	Vector3(0, 70, 0),
	Vector3(0, -40, 50),
	
	Vector3(0, -20, 0), //N
	Vector3(0, 0, -50),
	Vector3(0, 0, -50),
	Vector3(0, 0, -50),
	Vector3(0, 0, -50),
	Vector3(0, 0, 50),
	Vector3(0, 0, 50),
	Vector3(0, 0, 50),
	Vector3(0, 0, 50),
	Vector3(0, -40, -50),
	Vector3(0, -40, -50),
	Vector3(0, -40, -50),
	Vector3(0, 0, 50),
	Vector3(0, 0, 50),
	Vector3(0, 0, 50),
	Vector3(0, 0, 50)
};

int main() {
	puts("========================================");
	puts("Professional CS-GO cheat client (v 69.1)");
	puts("========================================");
	puts("Did you use \"-insecure\" flag while running CS-GO??? Close this now if you didn't!");

	Sleep(1000);

	puts("Opening process memory now!");

	Sleep(1000);


	hwnd = FindWindowA(NULL, CSGO_WINDOW_NAME);
	GetWindowThreadProcessId(hwnd, &procId); 
	moduleBase = GetModuleBaseAddress("client.dll"); 
	hProcess = OpenProcess(PROCESS_ALL_ACCESS, NULL, procId); 
	hdc = GetDC(hwnd);

	puts("Starting cheat...");
	puts("Instructions: Press & Hold DELETE in-game to activate aimbot");
	puts("              Press END to close program.");

	while (!GetAsyncKeyState(VK_END)) { //press the "end" key to end the hack
		vm = RPM<view_matrix_t>(moduleBase + dwViewMatrix);

		if (GetAsyncKeyState(VK_DELETE)) //press the "delete" key to activate the hack
		{
			Vector3 headPos = get_head(GetLocalPlayer());
			Vector3 reference = Vector3(headPos.x + 100.0f, headPos.y, headPos.z);

			for (int i = 0; i < sizeof(targets) / sizeof(Vector3) && GetAsyncKeyState(VK_DELETE); i++)
			{
				Vector3 target = WorldToScreen(Vector3(reference.x + targets[i].x, reference.y + targets[i].y, reference.z + targets[i].z), vm);
				SetCursorPos(target.x, target.y);
				Shoot();

				Sleep(200);
			}
		}
	}

	return 0;
}
