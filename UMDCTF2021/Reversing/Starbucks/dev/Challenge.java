
public class Challenge {
	
	
	public static String f1(String s) {
		StringBuilder b = new StringBuilder();
		char[] arr = s.toCharArray();
		for (int i = 0; i < arr.length; i++) {
			b.append((char) (arr[i] + i));
		}
		
		return b.toString();
	}
	
	public static String f1_rev(String s) {
		StringBuilder b = new StringBuilder();
		char[] arr = s.toCharArray();
		for (int i = 0; i < arr.length; i++) {
			b.append((char) (arr[i] - i));
		}
		
		return b.toString();
	}
	
	public static String f2(String s) {
		int half = s.length()/2;
		return s.substring(half+1) + s.substring(0, half+1);
	}
	
	public static String f3() {
		return f1(f2("$aQ\"cNP `_[eULB@PA'thpj]"));
	}

	public static void main(String[] args) {
		System.out.println("You really thought finding the flag would be so easy?");

	}
	
	

}
