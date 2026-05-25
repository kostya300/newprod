#include <iostream>
using namespace std;
int main(){

    int age;

    cin >> age;
    cout << "Мне " << age << " лет." << endl;
    if (age >= 18) {
    cout << "Доступ разрешён" << endl;
    }  else {
    cout << "Доступ запрещён" << endl;
    }
    return 0;
}

