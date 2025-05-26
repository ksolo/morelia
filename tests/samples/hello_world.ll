declare i32 @printf(i8*, ...)

@str_0 = private unnamed_addr constant [15 x i8] c"Hello, World!\0A\00", align 1

define i32 @main() {
entry:
  call i32 @printf(i8* getelementptr inbounds ([15 x i8], [15 x i8]* @str_0, i32 0, i32 0))
  ret i32 0
}