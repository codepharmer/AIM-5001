#include<bits/stdc++.h>

using namespace std;

int main()
{
    vector<vector<int>> m1;
    vector<vector<int>> m2;
    vector<int> row;
    for(int i=0; i < 100; i++) {
        for(int j=0; j < 100; j++)
            row.push_back(i);
            m1.push_back(row);
        row.clear();
    }
    int m1Size = m1.size();
    for(int i=0; i < m1Size; i++) {
        for(int j=0; j < m1Size; j++) {
          long newSum = 0;
        }
    }
    cout<<*row.begin();
    cout<<endl;
    return 0;
}