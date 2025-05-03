#include <functional>
#include <span>
#include <iostream>
#include <utility>
#include <random>

template<typename F, typename G, typename... Args>
auto compose(F f, G g, Args... args) -> decltype(f(g)) {
	return f(g(std::forward(args...)));
}

template<typename F, typename A, typename B>
A foldr(F const& f, A acc, std::span<B> bs) {
	if (bs.empty()) {
		return acc;
	} else {
		return f(bs[0], foldr<F, A, B>(f, acc, bs.subspan(1)));
	}
}

template<typename F, typename A, typename B>
A foldl(F const& f, A acc, std::span<B> bs) {
	if (bs.empty()) {
		return acc;
	} else {
		return foldl(f, f(bs[0], acc), bs.subspan(1));
	}
}

auto startsWithHelper(char c, std::function<bool(std::span<char>)> g) -> std::function<bool(std::span<char>)> {
	return [g, c] (std::span<char> sp) {
		bool b = g(sp.subspan(1));
		if (sp.empty()) {
			return false; // prevent obvious side channel?
		} else if (sp[0] == c) {
			return b;
		} else {
			return false;
		}
	};
}

template <typename T, typename U> 
std::function<U(T)> const_(U u) {
	return [u](T t) { return u; };
}

auto startsWith(std::string s1) {
	return foldr(std::function(startsWithHelper), const_<std::span<char>>(true), std::span(s1));
}

std::function<int(int)> subN(int i) {
	if (i == 0) {
		return [](int j) { return j; };
	} else {
		return [i](int j) { return subN(i-1)(j) - 1; };
	}
}

template <typename F, typename T>
void map_in_place(F const& f, std::span<T> xs) {
	if (xs.empty()) {
		return;
	}
	xs[0] = f(xs[0]);
	map_in_place(f, xs.subspan(1));
}

std::function<void(std::string&)> drop_str(int i) {
	if (i == 0) {
		return [](std::string& s) {};
	} else {
		return [i](std::string& s) {
			s.erase(0,1);
			drop_str(i-1)(s);
		};
	}
}

std::string reverse(std::string s) {
	return std::get<0>(foldr([](char c, std::tuple<std::string, size_t> acc) { std::get<0>(acc)[std::get<1>(acc)] = c; return std::tuple(std::get<0>(acc), std::get<1>(acc)+1); }, std::tuple(std::string(s.length(), ' '), 0), std::span(s)));
}


std::vector<std::string> chunk(std::string s, size_t n) {
	if (s.length() <= n) {
		return std::vector<std::string>{s};
	} else {
		auto rest = chunk(s.substr(3), n);
		rest.push_back(s.substr(0,3));
		return rest;
	}
}

std::string expand(std::pair<char, short> p) {
	char c = p.first;
	short s = p.second;
	char* s_ = (char*)&s;
	std::string str{s_[0], c, s_[1]};
	return str;
}

std::function<bool(std::vector<std::string>&)> build_compare(std::vector<std::pair<char, short>>& keys, std::mt19937& gen) {
	if (keys.empty()) {
		return const_<std::vector<std::string>&>(true);
	}
	int max = keys.size();
	std::uniform_int_distribution<> distribution{0, max-1};
	int index = distribution(gen);
	//std::cout << index << std::endl;

	std::string cmp = expand(keys[index]);
	keys.erase(keys.begin() + index);
	return [index, &keys, cmp, &gen](std::vector<std::string>& chunks) { bool b = cmp == chunks[index]; chunks.erase(chunks.begin() + index); return build_compare(keys, gen)(chunks) && b; };
}

int main() {
	std::string s;
	std::cout << "Enter flag: ";
	std::cin >> s;
	s = reverse(s);
	if (!startsWith("}eg")(s)) {
		std::cout << "stupid imperative programmer!!!!!!" << std::endl;
		return 0;
	}
	drop_str(3)(s);
	map_in_place(subN(5), std::span(s));
	s = reverse(s);
	auto v = chunk(s, 3);

	std::vector<std::pair<char, short>> keys;
	keys.push_back(std::make_pair('p', 23650));
	keys.push_back(std::make_pair('\\', 26983));
	keys.push_back(std::make_pair('g', 23132));
	keys.push_back(std::make_pair('j', 26980));
	keys.push_back(std::make_pair('^', 28521));
	keys.push_back(std::make_pair('a', 28762));
	keys.push_back(std::make_pair('\\', 26473));
	keys.push_back(std::make_pair('d', 27247));
	keys.push_back(std::make_pair('i', 24176));
	keys.push_back(std::make_pair('n', 24948));
	keys.push_back(std::make_pair('Z', 24431));
	keys.push_back(std::make_pair('j', 28264));
	keys.push_back(std::make_pair('`', 23139));
	keys.push_back(std::make_pair('Z', 28526));
	keys.push_back(std::make_pair('Z', 25638));
	keys.push_back(std::make_pair('^', 9846));
	keys.push_back(std::make_pair('O', 16702));
	keys.push_back(std::make_pair('H', 16208));

	std::mt19937 gen{std::random_device{}()};
	if (build_compare(keys, gen)(v)) {
		std::cout << "yuor did it!" << std::endl;
	} else {
		std::cout << "stupid imperative programmer!!!!!!" << std::endl;
	}

}
